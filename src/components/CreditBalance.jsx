/**
 * Componente de Balance de Créditos API
 * Muestra créditos disponibles, uso reciente y opción de recarga
 * Solo para usuarios HR_PRO_PLAN
 */
import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  TrendingUp, 
  Download, 
  AlertCircle,
  RefreshCw,
  DollarSign,
  Check
} from 'lucide-react';
import { api } from '../services/api';

const CreditBalance = () => {
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [selectedPack, setSelectedPack] = useState(null);

  // Packs de créditos disponibles
  const creditPacks = [
    {
      credits: 100,
      price: 9.99,
      perCredit: 0.0999,
      popular: false,
      savings: null
    },
    {
      credits: 500,
      price: 39.99,
      perCredit: 0.0799,
      popular: true,
      savings: '20%'
    },
    {
      credits: 1000,
      price: 69.99,
      perCredit: 0.0699,
      popular: false,
      savings: '30%'
    },
    {
      credits: 5000,
      price: 299.99,
      perCredit: 0.0599,
      popular: false,
      savings: '40%'
    }
  ];

  useEffect(() => {
    loadBalance();
    loadTransactions();
  }, []);

  const loadBalance = async () => {
    try {
      const data = await api.billing.getCreditBalance();
      setBalance(data);
    } catch (error) {
      console.error('Error loading balance:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTransactions = async () => {
    try {
      const data = await api.billing.getTransactions(10);
      setTransactions(data);
    } catch (error) {
      console.error('Error loading transactions:', error);
    }
  };

  const handleBuyCredits = async (pack) => {
    try {
      setLoading(true);
      const response = await api.billing.createCreditsCheckout(pack.credits);
      
      // Redirigir a Stripe Checkout
      window.location.href = response.url;
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('Error al crear sesión de pago. Por favor intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'credit_purchase':
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'api_usage':
        return <Download className="w-5 h-5 text-blue-500" />;
      case 'subscription':
        return <CreditCard className="w-5 h-5 text-purple-500" />;
      default:
        return <DollarSign className="w-5 h-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  const usagePercentage = balance ? (balance.api_credits_used / (balance.api_credits + balance.api_credits_used) * 100) : 0;
  const lowBalance = balance && balance.api_credits < 100;

  return (
    <div className="space-y-6">
      {/* Header con balance principal */}
      <div className="bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">Balance de Créditos API</h2>
            <p className="text-purple-200">Usa créditos para exportar datasets y acceder a la API</p>
          </div>
          <CreditCard className="w-12 h-12 text-purple-300" />
        </div>

        {/* Balance grande */}
        <div className="mb-6">
          <div className="text-6xl font-bold mb-2">
            {balance?.api_credits?.toLocaleString() || 0}
          </div>
          <div className="text-purple-200 text-lg">
            créditos disponibles
          </div>
        </div>

        {/* Barra de progreso */}
        <div className="mb-6">
          <div className="flex justify-between text-sm mb-2">
            <span>Usados: {balance?.api_credits_used?.toLocaleString() || 0}</span>
            <span>{usagePercentage.toFixed(1)}% utilizado</span>
          </div>
          <div className="w-full bg-purple-950 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Alerta de balance bajo */}
        {lowBalance && (
          <div className="bg-yellow-500 bg-opacity-20 border border-yellow-400 rounded-lg p-4 flex items-start gap-3 mb-6">
            <AlertCircle className="w-5 h-5 text-yellow-300 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-yellow-300">Balance bajo</p>
              <p className="text-sm text-yellow-200">
                Tienes menos de 100 créditos. Recarga para no interrumpir tus operaciones.
              </p>
            </div>
          </div>
        )}

        {/* Botón de recarga */}
        <button
          onClick={() => setShowBuyModal(true)}
          className="w-full bg-white text-purple-900 py-4 rounded-xl font-semibold hover:bg-purple-50 transition-colors flex items-center justify-center gap-2 shadow-lg"
        >
          <RefreshCw className="w-5 h-5" />
          Recargar Créditos
        </button>
      </div>

      {/* Historial de uso reciente */}
      <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-blue-500" />
          Uso Reciente
        </h3>

        {transactions.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <Download className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No hay transacciones recientes</p>
          </div>
        ) : (
          <div className="space-y-3">
            {transactions.map((tx) => (
              <div
                key={tx.id}
                className="flex items-center justify-between p-4 bg-gray-700 rounded-lg hover:bg-gray-650 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {getTransactionIcon(tx.transaction_type)}
                  <div>
                    <p className="font-medium text-white">
                      {tx.description || tx.transaction_type}
                    </p>
                    <p className="text-sm text-gray-400">
                      {formatDate(tx.created_at)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-bold ${tx.credits_purchased > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {tx.credits_purchased > 0 ? '+' : '-'}{Math.abs(tx.credits_purchased)}
                  </p>
                  {tx.amount && (
                    <p className="text-sm text-gray-400">
                      ${tx.amount.toFixed(2)}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Costo por operación */}
      <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-bold text-white mb-4">Costo por Operación</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Registro individual</p>
            <p className="text-2xl font-bold text-white">1 crédito</p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Dataset completo</p>
            <p className="text-2xl font-bold text-white">10 créditos</p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Análisis IA</p>
            <p className="text-2xl font-bold text-white">5 créditos</p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-1">Market Report</p>
            <p className="text-2xl font-bold text-white">20 créditos</p>
          </div>
        </div>
      </div>

      {/* Modal de compra de créditos */}
      {showBuyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Recargar Créditos API</h2>
                <button
                  onClick={() => setShowBuyModal(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>
              <p className="text-gray-400 mt-2">
                Selecciona el pack que mejor se adapte a tus necesidades
              </p>
            </div>

            <div className="p-6 grid md:grid-cols-2 gap-4">
              {creditPacks.map((pack) => (
                <div
                  key={pack.credits}
                  className={`relative border-2 rounded-xl p-6 cursor-pointer transition-all ${
                    pack.popular
                      ? 'border-purple-500 bg-purple-900 bg-opacity-20'
                      : 'border-gray-600 bg-gray-700 hover:border-purple-400'
                  }`}
                  onClick={() => setSelectedPack(pack)}
                >
                  {pack.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-purple-600 text-white text-xs font-bold rounded-full">
                      MÁS POPULAR
                    </div>
                  )}

                  <div className="text-center mb-4">
                    <p className="text-4xl font-bold text-white mb-2">
                      {pack.credits.toLocaleString()}
                    </p>
                    <p className="text-gray-400">créditos API</p>
                  </div>

                  <div className="text-center mb-4">
                    <p className="text-3xl font-bold text-purple-400">
                      ${pack.price}
                    </p>
                    <p className="text-sm text-gray-400 mt-1">
                      ${pack.perCredit.toFixed(4)} por crédito
                    </p>
                  </div>

                  {pack.savings && (
                    <div className="bg-green-500 bg-opacity-20 border border-green-500 rounded-lg p-2 mb-4 text-center">
                      <p className="text-green-400 font-semibold">
                        Ahorras {pack.savings}
                      </p>
                    </div>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleBuyCredits(pack);
                    }}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
                  >
                    <Check className="w-5 h-5" />
                    Comprar Ahora
                  </button>
                </div>
              ))}
            </div>

            <div className="p-6 bg-gray-900 border-t border-gray-700">
              <p className="text-sm text-gray-400 text-center">
                💳 Pago seguro procesado por Stripe • Los créditos se añaden instantáneamente
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreditBalance;
