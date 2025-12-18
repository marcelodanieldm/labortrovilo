/**
 * Dashboard de Sistema de Referidos
 * Muestra código único, estadísticas y recompensas
 */
import React, { useState, useEffect } from 'react';
import { 
  Copy, 
  Share2, 
  Users, 
  Gift, 
  TrendingUp,
  Award,
  CheckCircle,
  Clock,
  Twitter,
  Facebook,
  Linkedin,
  Mail
} from 'lucide-react';
import { api } from '../services/api';

const ReferralDashboard = () => {
  const [referralInfo, setReferralInfo] = useState(null);
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadReferralData();
  }, []);

  const loadReferralData = async () => {
    try {
      setLoading(true);
      const [info, statsData, leaderboardData, historyData] = await Promise.all([
        api.referral.getInfo(),
        api.referral.getStats(),
        api.referral.getLeaderboard(),
        api.referral.getHistory()
      ]);
      
      setReferralInfo(info);
      setStats(statsData);
      setLeaderboard(leaderboardData.leaderboard);
      setHistory(historyData.referrals);
    } catch (error) {
      console.error('Error loading referral data:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyReferralLink = () => {
    if (referralInfo) {
      navigator.clipboard.writeText(referralInfo.referral_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const shareOnSocial = (platform) => {
    if (!referralInfo) return;
    
    const text = `🚀 ¡Únete a Labortrovilo y recibe 50 créditos API gratis! Usa mi código: ${referralInfo.referral_code}`;
    const url = referralInfo.referral_url;
    
    const shareUrls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
      email: `mailto:?subject=Únete a Labortrovilo&body=${encodeURIComponent(text + '\n\n' + url)}`
    };
    
    window.open(shareUrls[platform], '_blank', 'width=600,height=400');
  };

  const getBadgeColor = (badge) => {
    if (badge.includes('Diamante')) return 'text-cyan-400';
    if (badge.includes('Platino')) return 'text-purple-400';
    if (badge.includes('Oro')) return 'text-yellow-400';
    if (badge.includes('Plata')) return 'text-gray-300';
    if (badge.includes('Bronce')) return 'text-orange-400';
    return 'text-gray-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4 flex items-center justify-center gap-3">
            <Gift className="w-10 h-10 text-indigo-500" />
            Sistema de Referidos
          </h1>
          <p className="text-xl text-gray-300">
            Invita a tus amigos y ambos reciben 50 créditos API gratis 🎉
          </p>
        </div>

        {/* Main Card - Referral Code */}
        <div className="bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 rounded-2xl p-8 mb-8 shadow-2xl">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-2">Tu Código de Referido</h2>
              <p className="text-purple-200 mb-4">
                Comparte este código o link con tus amigos
              </p>
              
              {/* Código grande */}
              <div className="bg-gray-900 bg-opacity-50 rounded-xl p-6 mb-4 border-2 border-indigo-400">
                <p className="text-5xl font-bold text-center text-indigo-300 tracking-wider">
                  {referralInfo?.referral_code}
                </p>
              </div>
              
              {/* URL de referido */}
              <div className="flex items-center gap-2 bg-gray-800 rounded-lg p-4">
                <input
                  type="text"
                  readOnly
                  value={referralInfo?.referral_url}
                  className="flex-1 bg-transparent text-white outline-none"
                />
                <button
                  onClick={copyReferralLink}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {copied ? (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      Copiado!
                    </>
                  ) : (
                    <>
                      <Copy className="w-5 h-5" />
                      Copiar
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 text-center border border-indigo-400">
                <Users className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-white">{referralInfo?.total_referrals}</p>
                <p className="text-sm text-gray-300">Referidos</p>
              </div>
              <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6 text-center border border-green-400">
                <Gift className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-white">{referralInfo?.referral_credits_earned}</p>
                <p className="text-sm text-gray-300">Créditos Ganados</p>
              </div>
            </div>
          </div>

          {/* Social Share Buttons */}
          <div className="mt-6 pt-6 border-t border-purple-700">
            <p className="text-white font-semibold mb-3 text-center">Compartir en redes:</p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <button
                onClick={() => shareOnSocial('twitter')}
                className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Twitter className="w-5 h-5" />
                Twitter
              </button>
              <button
                onClick={() => shareOnSocial('linkedin')}
                className="flex items-center gap-2 bg-blue-700 hover:bg-blue-800 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Linkedin className="w-5 h-5" />
                LinkedIn
              </button>
              <button
                onClick={() => shareOnSocial('facebook')}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Facebook className="w-5 h-5" />
                Facebook
              </button>
              <button
                onClick={() => shareOnSocial('email')}
                className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Mail className="w-5 h-5" />
                Email
              </button>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* Stats Card */}
          <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-indigo-500" />
              Tus Estadísticas
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <span className="text-gray-300">Total de Referidos</span>
                <span className="text-2xl font-bold text-white">{stats?.total_referrals}</span>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <span className="text-gray-300">Referidos Activos</span>
                <span className="text-2xl font-bold text-green-400">{stats?.active_referrals}</span>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <span className="text-gray-300">Este Mes</span>
                <span className="text-2xl font-bold text-indigo-400">{stats?.referrals_this_month}</span>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <span className="text-gray-300">Créditos Totales</span>
                <span className="text-2xl font-bold text-yellow-400">{stats?.credits_earned}</span>
              </div>

              {stats?.top_performer && (
                <div className="p-4 bg-gradient-to-r from-yellow-600 to-orange-600 rounded-lg">
                  <p className="text-white font-bold text-center flex items-center justify-center gap-2">
                    <Award className="w-6 h-6" />
                    🏆 ¡Top Performer!
                  </p>
                  <p className="text-yellow-100 text-sm text-center mt-1">
                    Estás en el top 10% de referidores
                  </p>
                </div>
              )}

              {stats?.leaderboard_position && (
                <div className="p-4 bg-gray-700 rounded-lg text-center">
                  <p className="text-gray-400 text-sm">Posición en Leaderboard</p>
                  <p className="text-3xl font-bold text-white">#{stats.leaderboard_position}</p>
                </div>
              )}
            </div>
          </div>

          {/* Leaderboard */}
          <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Award className="w-6 h-6 text-yellow-500" />
              Top Referidores
            </h3>

            <div className="space-y-3">
              {leaderboard.slice(0, 10).map((user, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between p-4 rounded-lg ${
                    idx < 3 ? 'bg-gradient-to-r from-yellow-900 to-orange-900' : 'bg-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`text-2xl font-bold ${
                      idx === 0 ? 'text-yellow-400' :
                      idx === 1 ? 'text-gray-300' :
                      idx === 2 ? 'text-orange-400' :
                      'text-gray-400'
                    }`}>
                      #{user.position}
                    </span>
                    <div>
                      <p className="font-semibold text-white">{user.name}</p>
                      <p className={`text-sm ${getBadgeColor(user.badge)}`}>
                        {user.badge}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-white">{user.total_referrals}</p>
                    <p className="text-sm text-gray-400">{user.credits_earned} créditos</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Referral History */}
        <div className="bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-500" />
            Tus Referidos ({history.length})
          </h3>

          {history.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">
                Aún no has referido a nadie. ¡Comparte tu código para empezar!
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-gray-700">
                    <th className="pb-3 px-4">Usuario</th>
                    <th className="pb-3 px-4">Fecha Registro</th>
                    <th className="pb-3 px-4">Tier</th>
                    <th className="pb-3 px-4">Estado</th>
                    <th className="pb-3 px-4">Créditos</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((referral) => (
                    <tr key={referral.id} className="border-b border-gray-700 hover:bg-gray-700 transition-colors">
                      <td className="py-4 px-4">
                        <p className="font-semibold text-white">{referral.full_name || referral.email}</p>
                        <p className="text-sm text-gray-400">{referral.email}</p>
                      </td>
                      <td className="py-4 px-4 text-gray-300">
                        {new Date(referral.joined_at).toLocaleDateString('es-ES')}
                        <p className="text-sm text-gray-500">{referral.days_active} días activo</p>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          referral.tier === 'HR_PRO_PLAN' ? 'bg-purple-600 text-white' :
                          referral.tier === 'CANDIDATO_PREMIUM' ? 'bg-blue-600 text-white' :
                          'bg-gray-600 text-gray-300'
                        }`}>
                          {referral.tier.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        {referral.is_validated ? (
                          <span className="flex items-center gap-2 text-green-400">
                            <CheckCircle className="w-5 h-5" />
                            Validado
                          </span>
                        ) : (
                          <span className="flex items-center gap-2 text-yellow-400">
                            <Clock className="w-5 h-5" />
                            Pendiente
                          </span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-xl font-bold text-green-400">
                          +{referral.credits_contributed}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* How it Works */}
        <div className="mt-8 bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">
            ¿Cómo funciona?
          </h3>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Share2 className="w-8 h-8 text-white" />
              </div>
              <h4 className="font-bold text-white mb-2">1. Comparte tu código</h4>
              <p className="text-gray-400">
                Comparte tu código único con amigos, colegas o en redes sociales
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h4 className="font-bold text-white mb-2">2. Ellos se registran</h4>
              <p className="text-gray-400">
                Tu amigo usa tu código al registrarse y recibe 50 créditos gratis
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Gift className="w-8 h-8 text-white" />
              </div>
              <h4 className="font-bold text-white mb-2">3. Ambos ganan</h4>
              <p className="text-gray-400">
                Recibes 50 créditos cuando tu referido se valida (7 días de actividad)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReferralDashboard;
