
# Autonom Trading — Event-Driven Hotfix (v2.9.1)

Bu paket, var olan mimarinizi **kademeli ve hibrit** bir şekilde **event-driven** akışa taşımak için minimal ama çalışır bir çekirdek sunar.

## Neler Var?

- **Event Bus** (sync, thread-safe)
- **BarDataEvent** ile **Replay-only BacktestingService**
- **FeatureService**: akış tabanlı rolling SMA & getiriler
- **StrategyService**: bar-bazlı sinyal (MA crossover)
- **RiskService**: pass-through risk + gross cap
- **PortfolioService**: gecikmeli pozisyon uygulaması ve equity curve
- **ReportingService**: Sharpe, Sortino, Max DD, CAGR + CSV çıktı

## Çalıştırma

```bash
pip install -r requirements.txt
python run_backtest.py
```

Bitince `equity_curve.csv` ve `metrics.csv` dosyaları oluşur.

## Entegrasyon Notları

- Bu paket **replay** motorunu `BacktestingService` içinde izole eder. Diğer tüm kararlar olaylar üzerinden akar.
- UI/Streamlit entegrasyonu için ReportingService çıktıları okunup görselleştirilebilir.

## Sonraki Adımlar (Öneri)

- Vol target & MaxDD constraint'lerini `RiskService` içine ekle
- Walk-forward (TSSplit) için `BacktestRequested` → birden fazla replay döngüsü
- Çoklu strateji/AI model adapter'ı ve sonuç kıyaslama event'leri
