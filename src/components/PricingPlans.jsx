/**
 * Componente de Pricing Plans
 * Compara los 3 tiers de suscripción con toggle mensual/anual
 */
import React, { useState, useEffect } from 'react';
import { Check, X, Zap, TrendingUp, Shield, Crown } from 'lucide-react';
import { api } from '../services/api';

const PricingPlans = () => {
  const [billingCycle, setBillingCycle] = useState('monthly'); // 'monthly' | 'yearly'
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentUserTier, setCurrentUserTier] = useState(null);

  useEffect(() => {
    loadPricing();
    loadCurrentUser();
  }, []);

  const loadPricing = async () => {
    try {
      const response = await api.billing.getPricing();
      setPricing(response);
    } catch (error) {
      console.error('Error loading pricing:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentUser = async () => {
    try {
      const user = await api.auth.getCurrentUser();
      setCurrentUserTier(user.subscription_tier);
    } catch (error) {
      console.log('Usuario no autenticado');
    }
  };

  const handleSubscribe = async (tier) => {
    if (tier === 'FREE') {
      alert('Ya tienes acceso al tier FREE');
      return;
    }

    if (tier === currentUserTier) {
      alert(`Ya tienes el plan ${tier}`);
      return;
    }

    try {
      setLoading(true);
      const response = await api.billing.createCheckoutSession(tier, billingCycle);
      
      // Redirigir a Stripe Checkout
      window.location.href = response.url;
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('Error al crear sesión de pago. Por favor intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const plans = [
    {
      id: 'FREE',
      name: 'Free',
      icon: Shield,
      color: 'text-gray-400',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      price: { monthly: 0, yearly: 0 },
      description: 'Para explorar oportunidades',
      features: [
        '5 búsquedas diarias',
        'Acceso básico a trabajos',
        'Filtros básicos',
        'Sin Intelligence Insights',
        'Sin alertas en tiempo real',
        'Sin Red Flags IA'
      ],
      available: [0, 1, 2],
      blocked: [3, 4, 5],
      cta: 'Plan Actual',
      popular: false
    },
    {
      id: 'CANDIDATO_PREMIUM',
      name: 'Candidato Premium',
      icon: Zap,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-500',
      price: { monthly: 19.99, yearly: 199.90 },
      description: 'Para candidatos serios',
      features: [
        'Búsquedas ilimitadas',
        'Alertas en tiempo real',
        'Red Flags IA detecta problemas',
        'Favoritos y guardar búsquedas',
        'Filtros avanzados',
        'Intelligence Insights'
      ],
      available: [0, 1, 2, 3, 4, 5],
      blocked: [],
      cta: 'Suscribirse',
      popular: true
    },
    {
      id: 'HR_PRO_PLAN',
      name: 'HR Professional',
      icon: Crown,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-500',
      price: { monthly: 99.99, yearly: 999.90 },
      description: 'Para reclutadores y empresas',
      features: [
        'Todo de PREMIUM',
        'API access completo',
        '1000 créditos API incluidos',
        'Datasets JSON/CSV export',
        'Hiring Signals en tiempo real',
        'Market Intelligence reports',
        'Bright Data integration'
      ],
      available: [0, 1, 2, 3, 4, 5, 6],
      blocked: [],
      cta: 'Suscribirse',
      popular: false
    }
  ];

  const yearlySavings = (plan) => {
    const monthlyCost = plan.price.monthly * 12;
    const yearlyCost = plan.price.yearly;
    const savings = ((monthlyCost - yearlyCost) / monthlyCost * 100).toFixed(0);
    return savings;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Elige el Plan Perfecto
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Desde exploración gratuita hasta herramientas profesionales de reclutamiento
          </p>

          {/* Toggle Mensual/Anual */}
          <div className="flex items-center justify-center gap-4">
            <span className={`text-lg ${billingCycle === 'monthly' ? 'text-white font-semibold' : 'text-gray-400'}`}>
              Mensual
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative inline-flex h-8 w-16 items-center rounded-full bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-9' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-lg ${billingCycle === 'yearly' ? 'text-white font-semibold' : 'text-gray-400'}`}>
              Anual
            </span>
            {billingCycle === 'yearly' && (
              <span className="ml-2 px-3 py-1 bg-green-500 text-white text-sm font-semibold rounded-full animate-pulse">
                Ahorra hasta 16%
              </span>
            )}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan) => {
            const Icon = plan.icon;
            const price = billingCycle === 'monthly' ? plan.price.monthly : plan.price.yearly;
            const isCurrentPlan = currentUserTier === plan.id;
            
            return (
              <div
                key={plan.id}
                className={`relative rounded-2xl border-2 ${plan.borderColor} ${plan.bgColor} p-8 shadow-xl transition-all hover:scale-105 ${
                  plan.popular ? 'ring-4 ring-blue-500 ring-opacity-50' : ''
                }`}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-blue-600 text-white text-sm font-bold rounded-full">
                    MÁS POPULAR
                  </div>
                )}

                {/* Current Plan Badge */}
                {isCurrentPlan && (
                  <div className="absolute top-4 right-4 px-3 py-1 bg-green-500 text-white text-xs font-semibold rounded-full">
                    Plan Actual
                  </div>
                )}

                {/* Icon & Name */}
                <div className="flex items-center gap-3 mb-4">
                  <Icon className={`w-8 h-8 ${plan.color}`} />
                  <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                </div>

                <p className="text-gray-600 mb-6">{plan.description}</p>

                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-bold text-gray-900">
                      ${price.toFixed(2)}
                    </span>
                    {plan.id !== 'FREE' && (
                      <span className="text-gray-500">
                        /{billingCycle === 'monthly' ? 'mes' : 'año'}
                      </span>
                    )}
                  </div>
                  {billingCycle === 'yearly' && plan.id !== 'FREE' && (
                    <p className="text-sm text-green-600 font-semibold mt-2">
                      Ahorras {yearlySavings(plan)}% vs. mensual
                    </p>
                  )}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleSubscribe(plan.id)}
                  disabled={isCurrentPlan || plan.id === 'FREE'}
                  className={`w-full py-3 px-6 rounded-lg font-semibold transition-all mb-8 ${
                    isCurrentPlan || plan.id === 'FREE'
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : plan.popular
                      ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
                      : 'bg-gray-800 text-white hover:bg-gray-700'
                  }`}
                >
                  {isCurrentPlan ? 'Plan Actual' : plan.cta}
                </button>

                {/* Features List */}
                <ul className="space-y-3">
                  {plan.features.map((feature, idx) => {
                    const isAvailable = plan.available.includes(idx);
                    return (
                      <li key={idx} className="flex items-start gap-3">
                        {isAvailable ? (
                          <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                        ) : (
                          <X className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                        )}
                        <span className={isAvailable ? 'text-gray-700' : 'text-gray-400 line-through'}>
                          {feature}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto bg-gray-800 rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-6">Preguntas Frecuentes</h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">¿Puedo cancelar en cualquier momento?</h3>
              <p className="text-gray-300">
                Sí, puedes cancelar tu suscripción cuando quieras. Seguirás teniendo acceso hasta el final del período pagado.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">¿Qué son los créditos API?</h3>
              <p className="text-gray-300">
                Los créditos API te permiten exportar datasets completos en JSON/CSV y usar la API programática. 
                1 crédito = 1 registro de trabajo, 10 créditos = dataset completo.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">¿Puedo cambiar de plan después?</h3>
              <p className="text-gray-300">
                Sí, puedes hacer upgrade o downgrade en cualquier momento. La diferencia se prorratea automáticamente.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">¿Qué métodos de pago aceptan?</h3>
              <p className="text-gray-300">
                Aceptamos todas las tarjetas de crédito/débito principales a través de Stripe. También PayPal y transferencias bancarias.
              </p>
            </div>
          </div>
        </div>

        {/* Trust Badges */}
        <div className="mt-12 flex flex-wrap items-center justify-center gap-8 text-gray-400">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            <span>Pago seguro con Stripe</span>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            <span>Facturación automática</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-5 h-5" />
            <span>Cancela cuando quieras</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPlans;
