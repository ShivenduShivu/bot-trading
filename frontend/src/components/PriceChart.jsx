import { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { getStockHistory } from '../utils/api';
import './PriceChart.css';

function PriceChart({ symbol }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [period, setPeriod] = useState('1mo');

  useEffect(() => {
    if (!symbol) return;

    // Initialize chart
    if (!chartRef.current && chartContainerRef.current) {
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { color: 'white' },
          textColor: '#2d3748',
        },
        grid: {
          vertLines: { color: '#e2e8f0' },
          horzLines: { color: '#e2e8f0' },
        },
        width: chartContainerRef.current.clientWidth,
        height: 400,
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });

      // Use addCandlestickSeries (correct method name)
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#48bb78',
        downColor: '#f56565',
        borderVisible: false,
        wickUpColor: '#48bb78',
        wickDownColor: '#f56565',
      });

      chartRef.current = chart;
      candlestickSeriesRef.current = candlestickSeries;

      // Handle resize
      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        if (chartRef.current) {
          chartRef.current.remove();
          chartRef.current = null;
        }
      };
    }
  }, []);

  useEffect(() => {
    if (symbol && candlestickSeriesRef.current) {
      loadChartData();
    }
  }, [symbol, period]);

  const loadChartData = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getStockHistory(symbol, period, '1d');
      
      if (!data || !data.data || data.data.length === 0) {
        setError('No chart data available');
        return;
      }

      // Transform data for lightweight-charts
      const chartData = data.data.map(item => ({
        time: item.date.split('T')[0], // Extract date part
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }));

      // Update chart
      if (candlestickSeriesRef.current) {
        candlestickSeriesRef.current.setData(chartData);
        
        // Fit content
        if (chartRef.current) {
          chartRef.current.timeScale().fitContent();
        }
      }

    } catch (err) {
      setError('Failed to load chart data');
      console.error('Chart error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
  };

  if (!symbol) {
    return (
      <div className="price-chart-empty">
        <p>Search and select a stock to view price chart</p>
      </div>
    );
  }

  return (
    <div className="price-chart-container">
      <div className="chart-header">
        <h3>{symbol} Price Chart</h3>
        <div className="period-selector">
          <button
            className={period === '1d' ? 'active' : ''}
            onClick={() => handlePeriodChange('1d')}
          >
            1D
          </button>
          <button
            className={period === '5d' ? 'active' : ''}
            onClick={() => handlePeriodChange('5d')}
          >
            5D
          </button>
          <button
            className={period === '1mo' ? 'active' : ''}
            onClick={() => handlePeriodChange('1mo')}
          >
            1M
          </button>
          <button
            className={period === '3mo' ? 'active' : ''}
            onClick={() => handlePeriodChange('3mo')}
          >
            3M
          </button>
          <button
            className={period === '6mo' ? 'active' : ''}
            onClick={() => handlePeriodChange('6mo')}
          >
            6M
          </button>
          <button
            className={period === '1y' ? 'active' : ''}
            onClick={() => handlePeriodChange('1y')}
          >
            1Y
          </button>
        </div>
      </div>

      {loading && (
        <div className="chart-loading">Loading chart data...</div>
      )}

      {error && (
        <div className="chart-error">{error}</div>
      )}

      <div 
        ref={chartContainerRef} 
        className="chart-canvas"
      />
    </div>
  );
}

export default PriceChart;