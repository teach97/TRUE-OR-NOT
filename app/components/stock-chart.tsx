"use client";

import { useEffect, useRef } from 'react';
import { AreaSeries, HistogramSeries, createChart } from 'lightweight-charts';
import type { UTCTimestamp } from 'lightweight-charts';
import type { MarketContext } from '../lib/fact-check-contract';

export default function StockChart({market}: {market: MarketContext}) {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host || market.candles.length === 0) return;
    const rising = (market.changePercent ?? 0) >= 0;
    const line = rising ? '#34d399' : '#f87171';
    const chart = createChart(host, {
      width: host.clientWidth,
      height: 220,
      layout: {
        background: {color: 'transparent'},
        textColor: '#8b959e',
        attributionLogo: true,
      },
      grid: {
        vertLines: {color: 'rgba(255, 255, 255, .04)'},
        horzLines: {color: 'rgba(255, 255, 255, .04)'},
      },
      rightPriceScale: {borderVisible: false},
      timeScale: {borderVisible: false},
    });
    const trend = chart.addSeries(AreaSeries, {
      lineColor: line,
      topColor: rising ? 'rgba(52, 211, 153, .28)' : 'rgba(248, 113, 113, .28)',
      bottomColor: 'rgba(52, 211, 153, 0)',
      priceLineVisible: false,
    });
    trend.setData(market.candles.map(candle => ({time: candle.time as UTCTimestamp, value: candle.close})));
    const volume = chart.addSeries(HistogramSeries, {priceScaleId: 'vol'});
    volume.setData(market.candles.map(candle => ({time: candle.time as UTCTimestamp, value: candle.volume ?? 0})));
    chart.priceScale('vol').applyOptions({scaleMargins: {top: 0.85, bottom: 0}});
    const observer = new ResizeObserver(() => chart.applyOptions({width: host.clientWidth}));
    observer.observe(host);
    return () => {observer.disconnect(); chart.remove();};
  }, [market]);

  const change = market.changePercent;
  return <div className="market-chart">
    <div className="market-chart-head">
      <strong>{market.displayName || market.symbol}</strong>
      <span className="market-chart-symbol">{market.symbol}</span>
      {typeof change === 'number' && <span className={`market-change ${change >= 0 ? 'is-up' : 'is-down'}`}>{change >= 0 ? '+' : ''}{change}%</span>}
    </div>
    <div ref={hostRef} className="market-chart-body" role="img" aria-label={`${market.symbol} 주가 추이 차트`}/>
    <p className="source-caption">최근 주가 흐름 참고용입니다. 지연 시세일 수 있으며 매수·매도 권고가 아닙니다. 차트: <a href="https://www.tradingview.com/" target="_blank" rel="noopener noreferrer">TradingView</a></p>
  </div>;
}
