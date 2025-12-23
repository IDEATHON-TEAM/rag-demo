import { useState } from 'react';
import { Wallet, Upload, Brain, Database, Zap, Shield, Network, Sparkles } from 'lucide-react';

export default function App() {
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');

  const connectWallet = async () => {
    // 模拟钱包连接
    // 在实际应用中，这里会调用 window.ethereum 来连接 MetaMask 或其他钱包
    try {
      // 模拟连接延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      const mockAddress = '0x' + Math.random().toString(16).substring(2, 42).toUpperCase();
      setWalletAddress(mockAddress);
      setWalletConnected(true);
    } catch (error) {
      console.error('连接钱包失败:', error);
    }
  };

  const disconnectWallet = () => {
    setWalletConnected(false);
    setWalletAddress('');
  };

  const features = [
    {
      icon: Brain,
      title: 'AI检索增强',
      description: '利用RAG技术，智能检索和生成知识内容，提供精准的问答服务',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: Database,
      title: '去中心化存储',
      description: '知识资产存储在区块链上，确保数据安全、透明和永久保存',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Shield,
      title: '版权保护',
      description: '基于智能合约的知识产权保护，确保创作者权益不受侵犯',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Zap,
      title: '即时变现',
      description: '知识资产化，通过NFT和代币经济实现知识价值的即时变现',
      color: 'from-orange-500 to-red-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* 导航栏 */}
      <nav className="relative z-10 px-6 py-4 flex justify-between items-center border-b border-white/10 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <span className="text-white text-xl">Web3-RAG 知识平台</span>
        </div>
        
        <div className="flex items-center gap-4">
          {!walletConnected ? (
            <button
              onClick={connectWallet}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg transition-all duration-200 shadow-lg hover:shadow-purple-500/50"
            >
              <Wallet className="w-5 h-5" />
              <span>连接钱包</span>
            </button>
          ) : (
            <div className="flex items-center gap-3">
              <div className="px-4 py-2 bg-white/10 backdrop-blur-md rounded-lg border border-white/20">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-white text-sm">{walletAddress.substring(0, 6)}...{walletAddress.substring(38)}</span>
                </div>
              </div>
              <button
                onClick={disconnectWallet}
                className="px-4 py-2 text-white/70 hover:text-white transition-colors"
              >
                断开
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* 主内容 */}
      <main className="relative z-10 container mx-auto px-6 py-16">
        {/* Hero区域 */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl text-white mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400">
            让知识成为资产
          </h1>
          <p className="text-xl text-white/70 mb-8 max-w-2xl mx-auto">
            基于区块链和AI技术的知识资产化平台，将您的智慧转化为可交易的数字资产
          </p>
          
          {/* 知识上传入口 */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              disabled={!walletConnected}
              className={`flex items-center gap-3 px-8 py-4 rounded-xl shadow-2xl transition-all duration-300 ${
                walletConnected
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white hover:scale-105 cursor-pointer'
                  : 'bg-gray-600 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Upload className="w-6 h-6" />
              <span className="font-medium">上传知识资产</span>
            </button>
            
            <button
              disabled={!walletConnected}
              className={`flex items-center gap-3 px-8 py-4 rounded-xl shadow-2xl transition-all duration-300 ${
                walletConnected
                  ? 'bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/20 hover:scale-105 cursor-pointer'
                  : 'bg-gray-700 text-gray-400 border border-gray-600 cursor-not-allowed'
              }`}
            >
              <Network className="w-6 h-6" />
              <span className="font-medium">探索知识库</span>
            </button>
          </div>

          {!walletConnected && (
            <p className="mt-4 text-sm text-yellow-400/80 flex items-center justify-center gap-2">
              <Shield className="w-4 h-4" />
              <span>请先连接钱包以使用平台功能</span>
            </p>
          )}
        </div>

        {/* RAG功能介绍 */}
        <div className="mt-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl text-white mb-4">平台核心功能</h2>
            <p className="text-white/60">结合Web3与人工智能，打造全新的知识价值生态</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group relative p-6 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 hover:border-white/30 transition-all duration-300 hover:scale-105"
              >
                <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-4 group-hover:rotate-12 transition-transform duration-300`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl text-white mb-2">{feature.title}</h3>
                <p className="text-white/60 text-sm leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* RAG技术说明 */}
        <div className="mt-20 max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 backdrop-blur-md rounded-2xl border border-purple-500/20 p-8">
            <div className="flex items-start gap-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center flex-shrink-0">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-2xl text-white mb-4">什么是RAG（检索增强生成）？</h3>
                <p className="text-white/70 mb-4 leading-relaxed">
                  RAG是一种先进的AI技术，结合了信息检索和大语言模型的生成能力。在我们的平台上，RAG技术能够：
                </p>
                <ul className="space-y-2 text-white/70">
                  <li className="flex items-start gap-2">
                    <Zap className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                    <span>智能检索您上传的知识内容，快速定位相关信息</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Zap className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                    <span>基于检索结果生成准确、相关的回答和内容</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Zap className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                    <span>确保AI生成内容的可追溯性和版权归属</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Zap className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                    <span>让知识资产在AI时代发挥更大价值</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* 底部统计 */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-white/5 backdrop-blur-md rounded-xl border border-white/10">
            <div className="text-3xl text-white mb-2">10,000+</div>
            <div className="text-white/60">知识资产</div>
          </div>
          <div className="text-center p-6 bg-white/5 backdrop-blur-md rounded-xl border border-white/10">
            <div className="text-3xl text-white mb-2">5,000+</div>
            <div className="text-white/60">创作者</div>
          </div>
          <div className="text-center p-6 bg-white/5 backdrop-blur-md rounded-xl border border-white/10">
            <div className="text-3xl text-white mb-2">$1M+</div>
            <div className="text-white/60">交易额</div>
          </div>
        </div>
      </main>
    </div>
  );
}
