"""
Webhooks de Stripe para Labortrovilo
Maneja eventos de pagos y actualiza automáticamente la base de datos
"""
import logging
from typing import Any
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
import stripe

from src.dependencies import get_db_session
from src.payments import StripeManager, STRIPE_WEBHOOK_SECRET
from models import User, SubscriptionStatus, Transaction

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db_session)
):
    """
    Endpoint para recibir webhooks de Stripe
    
    Eventos manejados:
    - checkout.session.completed: Pago exitoso de suscripción o créditos
    - customer.subscription.updated: Cambio en suscripción
    - customer.subscription.deleted: Suscripción cancelada
    - invoice.payment_succeeded: Renovación exitosa
    - invoice.payment_failed: Fallo en renovación
    """
    if not STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET no configurado")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Obtener body raw
    payload = await request.body()
    
    # Verificar firma de Stripe
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Procesar evento
    event_type = event['type']
    data = event['data']['object']
    
    logger.info(f"Recibido evento de Stripe: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            await handle_checkout_completed(data, db)
        
        elif event_type == 'customer.subscription.updated':
            await handle_subscription_updated(data, db)
        
        elif event_type == 'customer.subscription.deleted':
            await handle_subscription_deleted(data, db)
        
        elif event_type == 'invoice.payment_succeeded':
            await handle_invoice_payment_succeeded(data, db)
        
        elif event_type == 'invoice.payment_failed':
            await handle_invoice_payment_failed(data, db)
        
        else:
            logger.info(f"Evento no manejado: {event_type}")
    
    except Exception as e:
        logger.error(f"Error procesando evento {event_type}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing event: {str(e)}")
    
    return {"status": "success"}


# ==================== EVENT HANDLERS ====================

async def handle_checkout_completed(session: Any, db: Session):
    """
    Maneja checkout.session.completed
    Se dispara cuando un pago es exitoso (suscripción o créditos)
    """
    logger.info(f"Processing checkout.session.completed: {session.id}")
    
    # Extraer metadata
    user_id = session.metadata.get("user_id")
    transaction_type = session.metadata.get("transaction_type", "subscription")
    
    if not user_id:
        logger.error("No user_id en metadata del checkout session")
        return
    
    # Obtener usuario
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        logger.error(f"Usuario {user_id} no encontrado")
        return
    
    stripe_manager = StripeManager(db)
    
    if transaction_type == "credit_purchase":
        # Compra de créditos API
        credits_amount = int(session.metadata.get("credits_amount", 0))
        payment_intent_id = session.payment_intent
        
        stripe_manager.add_credits_to_user(user, credits_amount, payment_intent_id)
        logger.info(f"Créditos agregados: {credits_amount} para user {user_id}")
    
    else:
        # Suscripción nueva
        subscription_id = session.subscription
        
        if subscription_id:
            # Obtener detalles completos de la suscripción
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Activar suscripción
            stripe_manager.activate_subscription(user, stripe_subscription)
            logger.info(f"Suscripción activada: {subscription_id} para user {user_id}")


async def handle_subscription_updated(subscription: Any, db: Session):
    """
    Maneja customer.subscription.updated
    Se dispara cuando cambia el estado de una suscripción
    """
    logger.info(f"Processing customer.subscription.updated: {subscription.id}")
    
    # Buscar usuario por stripe_subscription_id
    user = db.query(User).filter(
        User.stripe_subscription_id == subscription.id
    ).first()
    
    if not user:
        logger.warning(f"Usuario no encontrado para subscription {subscription.id}")
        return
    
    # Actualizar status
    stripe_status = subscription.status
    
    status_mapping = {
        "active": SubscriptionStatus.ACTIVE,
        "canceled": SubscriptionStatus.CANCELED,
        "past_due": SubscriptionStatus.PAST_DUE,
        "incomplete": SubscriptionStatus.INCOMPLETE,
        "trialing": SubscriptionStatus.TRIALING
    }
    
    new_status = status_mapping.get(stripe_status, SubscriptionStatus.ACTIVE)
    user.subscription_status = new_status
    
    # Si fue cancelada, verificar cancel_at_period_end
    if subscription.cancel_at_period_end:
        logger.info(f"Suscripción {subscription.id} se cancelará al final del período")
    
    # Actualizar registro de Subscription
    from models import Subscription as SubModel
    sub_record = db.query(SubModel).filter(
        SubModel.stripe_subscription_id == subscription.id
    ).first()
    
    if sub_record:
        sub_record.status = new_status
        sub_record.updated_at = datetime.utcnow()
    
    db.commit()
    logger.info(f"Suscripción actualizada: {subscription.id} - Status: {new_status.value}")


async def handle_subscription_deleted(subscription: Any, db: Session):
    """
    Maneja customer.subscription.deleted
    Se dispara cuando una suscripción se cancela definitivamente
    """
    logger.info(f"Processing customer.subscription.deleted: {subscription.id}")
    
    from datetime import datetime
    from models import SubscriptionTier, Subscription as SubModel
    
    # Buscar usuario
    user = db.query(User).filter(
        User.stripe_subscription_id == subscription.id
    ).first()
    
    if not user:
        logger.warning(f"Usuario no encontrado para subscription {subscription.id}")
        return
    
    # Revertir a FREE tier
    user.subscription_tier = SubscriptionTier.FREE
    user.subscription_status = SubscriptionStatus.CANCELED
    user.stripe_subscription_id = None
    user.daily_search_limit = 5  # Límite de FREE tier
    user.subscription_end_date = datetime.utcnow()
    
    # Actualizar registro de Subscription
    sub_record = db.query(SubModel).filter(
        SubModel.stripe_subscription_id == subscription.id
    ).first()
    
    if sub_record:
        sub_record.status = SubscriptionStatus.CANCELED
        sub_record.ended_at = datetime.utcnow()
        sub_record.updated_at = datetime.utcnow()
    
    db.commit()
    logger.info(f"Usuario {user.id} revertido a FREE tier")


async def handle_invoice_payment_succeeded(invoice: Any, db: Session):
    """
    Maneja invoice.payment_succeeded
    Se dispara cuando un pago de factura es exitoso (renovaciones)
    """
    logger.info(f"Processing invoice.payment_succeeded: {invoice.id}")
    
    subscription_id = invoice.subscription
    
    if not subscription_id:
        logger.info("Invoice no tiene subscription_id (pago único)")
        return
    
    # Buscar usuario
    user = db.query(User).filter(
        User.stripe_subscription_id == subscription_id
    ).first()
    
    if not user:
        logger.warning(f"Usuario no encontrado para subscription {subscription_id}")
        return
    
    # Asegurar que status sea ACTIVE
    user.subscription_status = SubscriptionStatus.ACTIVE
    
    # Crear registro de transacción
    transaction = Transaction(
        user_id=user.id,
        stripe_invoice_id=invoice.id,
        stripe_subscription_id=subscription_id,
        stripe_payment_intent_id=invoice.payment_intent,
        transaction_type="subscription",
        amount=invoice.amount_paid / 100,  # Convertir de centavos
        currency=invoice.currency,
        status="succeeded",
        description=f"Renovación de suscripción {user.subscription_tier.value}"
    )
    
    db.add(transaction)
    db.commit()
    
    logger.info(f"Renovación exitosa para user {user.id}")


async def handle_invoice_payment_failed(invoice: Any, db: Session):
    """
    Maneja invoice.payment_failed
    Se dispara cuando falla un pago de renovación
    """
    logger.info(f"Processing invoice.payment_failed: {invoice.id}")
    
    subscription_id = invoice.subscription
    
    if not subscription_id:
        return
    
    # Buscar usuario
    user = db.query(User).filter(
        User.stripe_subscription_id == subscription_id
    ).first()
    
    if not user:
        logger.warning(f"Usuario no encontrado para subscription {subscription_id}")
        return
    
    # Marcar como PAST_DUE
    user.subscription_status = SubscriptionStatus.PAST_DUE
    
    # Crear registro de transacción fallida
    transaction = Transaction(
        user_id=user.id,
        stripe_invoice_id=invoice.id,
        stripe_subscription_id=subscription_id,
        transaction_type="subscription",
        amount=invoice.amount_due / 100,
        currency=invoice.currency,
        status="failed",
        description=f"Fallo en renovación de suscripción {user.subscription_tier.value}"
    )
    
    db.add(transaction)
    db.commit()
    
    logger.warning(f"Fallo en renovación para user {user.id}")
    
    # TODO: Enviar email de notificación al usuario


if __name__ == "__main__":
    print("Módulo de webhooks de Stripe cargado correctamente")
