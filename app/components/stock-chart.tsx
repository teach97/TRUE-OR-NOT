"use client";

import { useEffect, useRef } from 'react';
import { CandlestickSeries, HistogramSeries, LineSeries, createChart } from 'lightweight-charts';
import type { UTCTimestamp } from 'lightweight-charts';
import type { MarketContext } from '../lib/fact-check-contract';

function movingAverage(values: Array<{time: UTCTimestamp; value: number}>, period: number) {
  const out: Array<{time: UTCTimestamp; value: number}> = [];
  let sum = 0;
  for (let index = 0; index < values.length; index++) {
    sum += values[index].value;
    if (index >= period) sum -= values[index - period].value;
    if (index >= period - 1) out.push({time: values[index].time, value: sum / period});
  }
  return out;
}

export default function StockChart({market}: {market: MarketContext}) {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host || market.candles.length === 0) return;
    const chart = createChart(host, {
      width: host.clientWidth,
      height: 260,
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
    const candles = chart.addSeries(CandlestickSeries, {
      upColor: '#ef5350',
      downColor: '#2962ff',
      wickUpColor: '#ef5350',
      wickDownColor: '#2962ff',
      borderVisible: false,
      priceLineVisible: false,
    });
    candles.setData(market.candles.map(candle => ({
      time: candle.time as UTCTimestamp,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    })));
    const closes = market.candles.map(candle => ({time: candle.time as UTCTimestamp, value: candle.close}));
    const maColors = ['#f5c518', '#9c27b0', '#26a69a'];
    [5, 20, 60].forEach((period, index) => {
      const line = chart.addSeries(LineSeries, {
        color: maColors[index],
        lineWidth: 1,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerVisible: false,
      });
      line.setData(movingAverage(closes, period));
    });
    const volume = chart.addSeries(HistogramSeries, {priceScaleId: 'vol'});
    volume.setData(market.candles.map(candle => ({
      time: candle.time as UTCTimestamp,
      value: candle.volume ?? 0,
      color: candle.close >= candle.open ? 'rgba(239, 83, 80, .5)' : 'rgba(41, 98, 255, .5)',
    })));
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
