"""
Sistema de Pagos y Monetización de Labortrovilo
Integración completa con Stripe para suscripciones y créditos API
"""
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import stripe

from sqlalchemy.orm import Session
from models import (
    User, 
    Subscription, 
    Transaction, 
    SubscriptionTier, 
    SubscriptionStatus,
    UserRole
)

# Configurar Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pricing Configuration (en centavos)
PRICING = {
    SubscriptionTier.FREE: {
        "monthly": 0,
        "yearly": 0,
        "daily_search_limit": 5,
        "api_credits": 0,
        "features": [
            "5 búsquedas diarias",
            "Acceso básico a ofertas",
            "Sin Intelligence Insights"
        ]
    },
    SubscriptionTier.CANDIDATO_PREMIUM: {
        "monthly": 1999,  # $19.99/mes
        "yearly": 19990,  # $199.90/año (2 meses gratis)
        "stripe_price_id_monthly": os.getenv("STRIPE_PRICE_CANDIDATO_MONTHLY", ""),
        "stripe_price_id_yearly": os.getenv("STRIPE_PRICE_CANDIDATO_YEARLY", ""),
        "daily_search_limit": 999999,  # Ilimitado
        "api_credits": 0,
        "features": [
            "Búsquedas ilimitadas",
            "Alertas en tiempo real",
            "Red Flags de IA",
            "Guardado de favoritos",
            "Filtros avanzados"
        ]
    },
    SubscriptionTier.HR_PRO_PLAN: {
        "monthly": 9999,  # $99.99/mes
        "yearly": 99990,  # $999.90/año (2 meses gratis)
        "stripe_price_id_monthly": os.getenv("STRIPE_PRICE_HR_PRO_MONTHLY", ""),
        "stripe_price_id_yearly": os.getenv("STRIPE_PRICE_HR_PRO_YEARLY", ""),
        "daily_search_limit": 999999,  # Ilimitado
        "api_credits": 1000,  # 1000 créditos iniciales al suscribirse
        "features": [
            "Todo de CANDIDATO_PREMIUM",
            "Acceso completo a la API",
            "1000 créditos API incluidos",
            "Descarga de datasets (JSON/CSV)",
            "Hiring Signals",
            "Market Intelligence Dashboard",
            "Bright Data integration"
        ]
    }
}

# Precios de créditos API adicionales
API_CREDITS_PRICING = {
    100: {"price": 999, "stripe_price_id": os.getenv("STRIPE_PRICE_CREDITS_100", "")},  # $9.99
    500: {"price": 3999, "stripe_price_id": os.getenv("STRIPE_PRICE_CREDITS_500", "")},  # $39.99
    1000: {"price": 6999, "stripe_price_id": os.getenv("STRIPE_PRICE_CREDITS_1000", "")},  # $69.99
    5000: {"price": 29999, "stripe_price_id": os.getenv("STRIPE_PRICE_CREDITS_5000", "")}  # $299.99
}


class StripeManager:
    """
    Gestor principal de operaciones con Stripe
    Maneja suscripciones, pagos y créditos API
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        if not stripe.api_key:
            logger.warning("Stripe API key no configurada")
    
    # ==================== CUSTOMERS ====================
    
    def create_customer(self, user: User) -> str:
        """
        Crea un customer en Stripe para un usuario
        
        Returns:
            stripe_customer_id
        """
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name or user.email,
                metadata={
                    "user_id": user.id,
                    "role": user.role.value
                }
            )
            
            # Guardar customer_id en user
            user.stripe_customer_id = customer.id
            self.db.commit()
            
            logger.info(f"Customer creado en Stripe: {customer.id} para user {user.id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creando customer en Stripe: {str(e)}")
            raise
    
    def get_or_create_customer(self, user: User) -> str:
        """
        Obtiene el customer_id existente o crea uno nuevo
        """
        if user.stripe_customer_id:
            return user.stripe_customer_id
        
        return self.create_customer(user)
    
    # ==================== SUBSCRIPTIONS ====================
    
    def create_checkout_session(
        self, 
        user: User, 
        tier: SubscriptionTier,
        interval: str = "month",
        success_url: str = "http://localhost:3000/success",
        cancel_url: str = "http://localhost:3000/pricing"
    ) -> Dict[str, Any]:
        """
        Crea una sesión de Stripe Checkout para suscripción
        
        Args:
            user: Usuario que se va a suscribir
            tier: Tier de suscripción (CANDIDATO_PREMIUM o HR_PRO_PLAN)
            interval: "month" o "year"
            success_url: URL de redirección exitosa
            cancel_url: URL de redirección cancelada
            
        Returns:
            Dict con url de checkout y session_id
        """
        if tier == SubscriptionTier.FREE:
            raise ValueError("FREE tier no requiere checkout")
        
        # Obtener o crear customer
        customer_id = self.get_or_create_customer(user)
        
        # Obtener price_id de Stripe
        price_id = PRICING[tier].get(f"stripe_price_id_{interval}")
        if not price_id:
            raise ValueError(f"No se encontró price_id para {tier.value} {interval}")
        
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    "user_id": user.id,
                    "tier": tier.value,
                    "interval": interval
                },
                subscription_data={
                    "metadata": {
                        "user_id": user.id,
                        "tier": tier.value
                    }
                }
            )
            
            logger.info(f"Checkout session creada: {checkout_session.id} para user {user.id}")
            
            return {
                "url": checkout_session.url,
                "session_id": checkout_session.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creando checkout session: {str(e)}")
            raise
    
    def activate_subscription(
        self, 
        user: User, 
        stripe_subscription: stripe.Subscription
    ) -> Subscription:
        """
        Activa una suscripción después de un pago exitoso
        Actualiza el usuario y crea registro en DB
        """
        try:
            # Extraer tier de metadata
            tier_str = stripe_subscription.metadata.get("tier")
            tier = SubscriptionTier[tier_str]
            
            # Actualizar usuario
            user.subscription_tier = tier
            user.subscription_status = SubscriptionStatus.ACTIVE
            user.stripe_subscription_id = stripe_subscription.id
            user.subscription_start_date = datetime.fromtimestamp(stripe_subscription.current_period_start)
            user.subscription_end_date = datetime.fromtimestamp(stripe_subscription.current_period_end)
            
            # Actualizar límites según tier
            user.daily_search_limit = PRICING[tier]["daily_search_limit"]
            
            # Si es HR_PRO, agregar créditos iniciales
            if tier == SubscriptionTier.HR_PRO_PLAN:
                initial_credits = PRICING[tier]["api_credits"]
                user.api_credits += initial_credits
                logger.info(f"Agregados {initial_credits} créditos API a user {user.id}")
            
            # Actualizar role si es necesario
            if tier == SubscriptionTier.HR_PRO_PLAN and user.role != UserRole.HR_PRO:
                user.role = UserRole.HR_PRO
            
            # Crear registro de suscripción
            subscription = Subscription(
                user_id=user.id,
                stripe_subscription_id=stripe_subscription.id,
                stripe_customer_id=stripe_subscription.customer,
                stripe_price_id=stripe_subscription.items.data[0].price.id,
                tier=tier,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                amount=stripe_subscription.items.data[0].price.unit_amount / 100,  # Convertir de centavos
                currency=stripe_subscription.currency,
                interval=stripe_subscription.items.data[0].price.recurring.interval
            )
            
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Suscripción activada: {subscription.id} para user {user.id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error activando suscripción: {str(e)}")
            self.db.rollback()
            raise
    
    def cancel_subscription(self, user: User, immediately: bool = False) -> bool:
        """
        Cancela la suscripción de un usuario
        
        Args:
            user: Usuario
            immediately: Si True, cancela inmediatamente. Si False, cancela al final del período
            
        Returns:
            True si se canceló exitosamente
        """
        if not user.stripe_subscription_id:
            raise ValueError("Usuario no tiene suscripción activa")
        
        try:
            if immediately:
                stripe.Subscription.delete(user.stripe_subscription_id)
                user.subscription_status = SubscriptionStatus.CANCELED
            else:
                stripe.Subscription.modify(
                    user.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                # Mantener status ACTIVE hasta el final del período
            
            # Actualizar registro en DB
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == user.stripe_subscription_id,
                Subscription.user_id == user.id
            ).first()
            
            if subscription:
                subscription.canceled_at = datetime.utcnow()
                if immediately:
                    subscription.status = SubscriptionStatus.CANCELED
                    subscription.ended_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Suscripción cancelada para user {user.id} (immediately={immediately})")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Error cancelando suscripción: {str(e)}")
            raise
    
    def update_subscription_tier(self, user: User, new_tier: SubscriptionTier) -> Subscription:
        """
        Actualiza el tier de suscripción de un usuario (upgrade/downgrade)
        """
        if not user.stripe_subscription_id:
            raise ValueError("Usuario no tiene suscripción activa")
        
        # Obtener price_id del nuevo tier
        # Detectar si es monthly o yearly
        current_subscription = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == user.stripe_subscription_id
        ).first()
        
        interval = current_subscription.interval if current_subscription else "month"
        new_price_id = PRICING[new_tier].get(f"stripe_price_id_{interval}")
        
        if not new_price_id:
            raise ValueError(f"No se encontró price_id para {new_tier.value}")
        
        try:
            # Obtener suscripción actual de Stripe
            stripe_sub = stripe.Subscription.retrieve(user.stripe_subscription_id)
            
            # Actualizar suscripción
            updated_sub = stripe.Subscription.modify(
                user.stripe_subscription_id,
                items=[{
                    'id': stripe_sub['items']['data'][0].id,
                    'price': new_price_id,
                }],
                metadata={
                    "tier": new_tier.value
                },
                proration_behavior='always_invoice'  # Prorratear cambios
            )
            
            # Actualizar en nuestra DB
            user.subscription_tier = new_tier
            user.daily_search_limit = PRICING[new_tier]["daily_search_limit"]
            
            # Si upgrade a HR_PRO, agregar créditos
            if new_tier == SubscriptionTier.HR_PRO_PLAN:
                user.api_credits += PRICING[new_tier]["api_credits"]
                if user.role != UserRole.HR_PRO:
                    user.role = UserRole.HR_PRO
            
            # Actualizar subscription record
            if current_subscription:
                current_subscription.tier = new_tier
                current_subscription.stripe_price_id = new_price_id
                current_subscription.amount = updated_sub.items.data[0].price.unit_amount / 100
                current_subscription.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(current_subscription)
            
            logger.info(f"Suscripción actualizada a {new_tier.value} para user {user.id}")
            return current_subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Error actualizando suscripción: {str(e)}")
            self.db.rollback()
            raise
    
    # ==================== API CREDITS ====================
    
    def create_credit_purchase_session(
        self,
        user: User,
        credits_amount: int,
        success_url: str = "http://localhost:3000/success",
        cancel_url: str = "http://localhost:3000/billing"
    ) -> Dict[str, Any]:
        """
        Crea sesión de checkout para compra de créditos API
        
        Args:
            user: Usuario
            credits_amount: Cantidad de créditos (100, 500, 1000, 5000)
            
        Returns:
            Dict con url y session_id
        """
        if credits_amount not in API_CREDITS_PRICING:
            raise ValueError(f"Cantidad de créditos inválida: {credits_amount}")
        
        customer_id = self.get_or_create_customer(user)
        price_id = API_CREDITS_PRICING[credits_amount]["stripe_price_id"]
        
        if not price_id:
            raise ValueError(f"No se encontró price_id para {credits_amount} créditos")
        
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',  # Pago único, no suscripción
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    "user_id": user.id,
                    "transaction_type": "credit_purchase",
                    "credits_amount": credits_amount
                }
            )
            
            logger.info(f"Credit purchase session creada: {checkout_session.id} para user {user.id}")
            
            return {
                "url": checkout_session.url,
                "session_id": checkout_session.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creando credit purchase session: {str(e)}")
            raise
    
    def add_credits_to_user(self, user: User, credits: int, transaction_id: str = None) -> User:
        """
        Agrega créditos API a un usuario
        
        Args:
            user: Usuario
            credits: Cantidad de créditos a agregar
            transaction_id: ID de transacción de Stripe
            
        Returns:
            User actualizado
        """
        try:
            user.api_credits += credits
            
            # Crear registro de transacción
            transaction = Transaction(
                user_id=user.id,
                stripe_payment_intent_id=transaction_id,
                transaction_type="credit_purchase",
                amount=API_CREDITS_PRICING.get(credits, {}).get("price", 0) / 100,
                currency="usd",
                status="succeeded",
                credits_purchased=credits,
                description=f"Compra de {credits} créditos API"
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Agregados {credits} créditos a user {user.id}. Total: {user.api_credits}")
            return user
            
        except Exception as e:
            logger.error(f"Error agregando créditos: {str(e)}")
            self.db.rollback()
            raise
    
    def deduct_credits(self, user: User, credits: int, description: str = "") -> bool:
        """
        Deduce créditos API del usuario
        
        Returns:
            True si se dedujo exitosamente, False si no tiene suficientes
        """
        if user.api_credits < credits:
            logger.warning(f"User {user.id} no tiene suficientes créditos. Tiene: {user.api_credits}, necesita: {credits}")
            return False
        
        try:
            user.api_credits -= credits
            user.api_credits_used += credits
            
            # Crear registro de transacción
            transaction = Transaction(
                user_id=user.id,
                transaction_type="credit_usage",
                amount=0,
                currency="usd",
                status="succeeded",
                credits_purchased=-credits,  # Negativo para indicar deducción
                description=description or f"Uso de {credits} créditos API"
            )
            
            self.db.add(transaction)
            self.db.commit()
            
            logger.info(f"Deducidos {credits} créditos de user {user.id}. Restantes: {user.api_credits}")
            return True
            
        except Exception as e:
            logger.error(f"Error deduciendo créditos: {str(e)}")
            self.db.rollback()
            raise
    
    # ==================== DAILY SEARCHES ====================
    
    def check_daily_search_limit(self, user: User) -> bool:
        """
        Verifica si el usuario puede realizar otra búsqueda hoy
        Resetea el contador si es un nuevo día
        
        Returns:
            True si puede buscar, False si alcanzó el límite
        """
        # Verificar si es un nuevo día
        now = datetime.utcnow()
        last_reset = user.last_search_reset or now
        
        if now.date() > last_reset.date():
            # Nuevo día, resetear contador
            user.daily_searches = 0
            user.last_search_reset = now
            self.db.commit()
        
        # Verificar límite
        can_search = user.daily_searches < user.daily_search_limit
        
        if not can_search:
            logger.warning(f"User {user.id} alcanzó límite diario de búsquedas ({user.daily_search_limit})")
        
        return can_search
    
    def increment_daily_searches(self, user: User):
        """
        Incrementa el contador de búsquedas diarias
        """
        user.daily_searches += 1
        self.db.commit()
        logger.info(f"User {user.id} realizó búsqueda {user.daily_searches}/{user.daily_search_limit}")
    
    # ==================== UTILITIES ====================
    
    def get_subscription_info(self, user: User) -> Dict[str, Any]:
        """
        Obtiene información completa de la suscripción del usuario
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        tier_info = PRICING.get(user.subscription_tier, {})
        
        return {
            "tier": user.subscription_tier.value,
            "status": user.subscription_status.value,
            "features": tier_info.get("features", []),
            "daily_search_limit": user.daily_search_limit,
            "daily_searches_used": user.daily_searches,
            "api_credits": user.api_credits,
            "api_credits_used": user.api_credits_used,
            "subscription_start": user.subscription_start_date.isoformat() if user.subscription_start_date else None,
            "subscription_end": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
            "stripe_subscription_id": user.stripe_subscription_id,
            "can_upgrade": user.subscription_tier != SubscriptionTier.HR_PRO_PLAN,
            "subscription_details": {
                "id": subscription.id if subscription else None,
                "amount": subscription.amount if subscription else 0,
                "currency": subscription.currency if subscription else "usd",
                "interval": subscription.interval if subscription else None
            } if subscription else None
        }
    
    def get_transaction_history(self, user: User, limit: int = 50) -> List[Transaction]:
        """
        Obtiene el historial de transacciones del usuario
        """
        return (
            self.db.query(Transaction)
            .filter(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )


# ==================== HELPER FUNCTIONS ====================

def get_pricing_info() -> Dict[str, Any]:
    """
    Retorna la información de pricing para mostrar en frontend
    """
    return {
        "tiers": {
            tier.value: {
                "name": tier.value,
                "monthly_price": info["monthly"] / 100,
                "yearly_price": info["yearly"] / 100,
                "daily_search_limit": info["daily_search_limit"],
                "api_credits": info["api_credits"],
                "features": info["features"]
            }
            for tier, info in PRICING.items()
        },
        "api_credits": {
            amount: {
                "credits": amount,
                "price": pricing["price"] / 100
            }
            for amount, pricing in API_CREDITS_PRICING.items()
        }
    }


if __name__ == "__main__":
    # Test básico
    print("Módulo de pagos Stripe cargado correctamente")
    print("Pricing tiers:", list(PRICING.keys()))
    print("API credits packs:", list(API_CREDITS_PRICING.keys()))
