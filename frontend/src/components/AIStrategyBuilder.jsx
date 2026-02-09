import { useState } from 'react';
import { runBacktest, generateStrategyFromAI, optimizeStrategy } from '../utils/api';
import BacktestResults from './BacktestResults';
import './AIStrategyBuilder.css';

function AIStrategyBuilder() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState('');
  const [aiResult, setAiResult] = useState(null);
  const [backtestResult, setBacktestResult] = useState(null);
  const [showOptimizations, setShowOptimizations] = useState(false);
  const [optimizations, setOptimizations] = useState(null);

  const handleGenerateStrategy = async () => {
    if (!prompt.trim()) {
      setError('Please describe your trading strategy');
      return;
    }

    setAiLoading(true);
    setError('');
    setAiResult(null);
    setBacktestResult(null);
    setShowOptimizations(false);

    try {
      const result = await generateStrategyFromAI(prompt);
      setAiResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  const handleRunBacktest = async () => {
    if (!aiResult) return;

    setLoading(true);
    setError('');

    try {
      // Calculate date range based on backtest_period
      const endDate = new Date().toISOString().split('T')[0];
      let startDate = new Date();
      
      switch (aiResult.backtest_period) {
        case '1mo':
          startDate.setMonth(startDate.getMonth() - 1);
          break;
        case '3mo':
          startDate.setMonth(startDate.getMonth() - 3);
          break;
        case '6mo':
          startDate.setMonth(startDate.getMonth() - 6);
          break;
        case '1y':
          startDate.setFullYear(startDate.getFullYear() - 1);
          break;
        default:
          startDate.setMonth(startDate.getMonth() - 6);
      }
      
      const backtestData = {
        strategy_type: aiResult.strategy_type,
        symbol: aiResult.symbol,
        parameters: aiResult.parameters,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate,
        initial_capital: 10000,
      };

      const result = await runBacktest(backtestData);
      setBacktestResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (!aiResult) return;

    setLoading(true);
    setError('');

    try {
      const result = await optimizeStrategy(
        aiResult.strategy_type,
        aiResult.symbol,
        aiResult.parameters
      );
      setOptimizations(result);
      setShowOptimizations(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = [
    "Create a bot that buys when RSI drops below 30 and sells above 70",
    "Build a moving average crossover strategy for Apple stock",
    "Make a MACD strategy for trading Tesla",
    "Buy tech stocks when they're oversold and sell when overbought",
  ];

  return (
    <div className="ai-strategy-builder">
      <div className="ai-builder-header">
        <h1>🤖 AI Strategy Builder</h1>
        <p>Describe your trading idea in plain English, and AI will build it for you!</p>
      </div>

      {/* AI Prompt Input */}
      <div className="ai-prompt-section">
        <div className="prompt-card">
          <label htmlFor="strategy-prompt">What trading strategy do you want?</label>
          <textarea
            id="strategy-prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Example: Create a bot that buys Apple when the 10-day moving average crosses above the 50-day moving average, and sells when it crosses below..."
            rows="4"
          />

          <div className="example-prompts">
            <p>💡 Try these examples:</p>
            <div className="example-chips">
              {examplePrompts.map((example, index) => (
                <button
                  key={index}
                  className="example-chip"
                  onClick={() => setPrompt(example)}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          <button
            className="generate-button"
            onClick={handleGenerateStrategy}
            disabled={aiLoading || !prompt.trim()}
          >
            {aiLoading ? '🤖 AI is thinking...' : '✨ Generate Strategy with AI'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {/* AI Generated Strategy */}
      {aiResult && (
        <div className="ai-result-section">
          <div className="strategy-card">
            <div className="strategy-header">
              <h2>📊 AI Generated Strategy</h2>
              <span className={`confidence-badge ${aiResult.confidence}`}>
                {aiResult.confidence} confidence
              </span>
            </div>

            <div className="strategy-details">
              <div className="detail-row">
                <span className="detail-label">Strategy Type:</span>
                <span className="detail-value">{aiResult.strategy_type.replace('_', ' ')}</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Stock Symbol:</span>
                <span className="detail-value">{aiResult.symbol}</span>
              </div>

              <div className="detail-row">
                <span className="detail-label">Backtest Period:</span>
                <span className="detail-value">{aiResult.backtest_period}</span>
              </div>

              <div className="parameters-section">
                <h3>Parameters:</h3>
                <div className="parameters-grid">
                  {Object.entries(aiResult.parameters).map(([key, value]) => (
                    <div key={key} className="parameter-item">
                      <span className="param-name">{key.replace('_', ' ')}:</span>
                      <span className="param-value">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="explanation-section">
                <h3>📖 How it works:</h3>
                <p>{aiResult.explanation}</p>
              </div>
            </div>

            <div className="strategy-actions">
              <button
                className="backtest-button"
                onClick={handleRunBacktest}
                disabled={loading}
              >
                {loading ? '⏳ Running Backtest...' : '🚀 Run Backtest'}
              </button>

              <button
                className="optimize-button"
                onClick={handleOptimize}
                disabled={loading}
              >
                {loading ? '⏳ Optimizing...' : '⚡ Optimize Parameters'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Optimization Suggestions */}
      {showOptimizations && optimizations && (
        <div className="optimizations-section">
          <h2>⚡ AI Optimization Suggestions</h2>
          <p className="optimization-intro">{optimizations.recommendation}</p>

          <div className="optimization-grid">
            {['conservative', 'balanced', 'aggressive'].map((type) => (
              optimizations[type] && (
                <div key={type} className={`optimization-card ${type}`}>
                  <h3>{type.charAt(0).toUpperCase() + type.slice(1)}</h3>
                  <div className="opt-parameters">
                    {Object.entries(optimizations[type])
                      .filter(([key]) => key !== 'explanation')
                      .map(([key, value]) => (
                        <div key={key} className="opt-param">
                          <span>{key}:</span>
                          <strong>{value}</strong>
                        </div>
                      ))}
                  </div>
                  <p className="opt-explanation">{optimizations[type].explanation}</p>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Backtest Results */}
      {backtestResult && (
        <BacktestResults results={backtestResult} />
      )}
    </div>
  );
}

export default AIStrategyBuilder;