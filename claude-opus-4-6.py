#!/usr/bin/env python3
"""
Trading Bot Autonome - Claude AI + MT4 (Pepperstone) + Trading212
Indicateurs: RSI, MACD, OB, FVG, DXY, FIBO
Timeframe: 4h | Lot: 0.1 | SL: 50 pips | TP: 100 pips
"""

import os
import time
import json
from datetime import datetime, timedelta
import logging
import requests
import MetaTrader5 as mt5
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import anthropic
import numpy as np
import pandas as pd
from talib import RSI, MACD, SMA
from scipy import stats

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration API & Credentials
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MT4_LOGIN = os.getenv("MT4_LOGIN")
MT4_PASSWORD = os.getenv("MT4_PASSWORD")
MT4_SERVER = os.getenv("MT4_SERVER", "Pepperstone-Demo")
TRADING212_EMAIL = os.getenv("TRADING212_EMAIL")
TRADING212_PASSWORD = os.getenv("TRADING212_PASSWORD")

# Config Trading
TIMEFRAME = "4h"
LOT_SIZE = 0.1
STOP_LOSS_PIPS = 50
TAKE_PROFIT_PIPS = 100
CHECK_INTERVAL = 3600  # 1 heure
SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

# Classe MT4
class MT4Handler:
    def __init__(self):
        self.initialized = False
        self.connect()
    
    def connect(self):
        """Connexion à MT4"""
        try:
            if not mt5.initialize(login=int(MT4_LOGIN), password=MT4_PASSWORD, server=MT4_SERVER):
                logger.error(f"MT4 initialization failed: {mt5.last_error()}")
                return False
            self.initialized = True
            logger.info("✅ MT4 connecté (Pepperstone)")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion MT4: {e}")
            return False
    
    def get_candles(self, symbol, timeframe_minutes=240):
        """Récupère les données OHLC"""
        try:
            if not self.initialized:
                return None
            
            tf = mt5.TIMEFRAME_H1 if timeframe_minutes == 60 else mt5.TIMEFRAME_H4
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, 100)
            
            if rates is None:
                logger.warning(f"Pas de données pour {symbol}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        
        except Exception as e:
            logger.error(f"Erreur récupération candles {symbol}: {e}")
            return None
    
    def place_order(self, symbol, order_type, volume, price, sl, tp):
        """Place un ordre MT4"""
        try:
            if not self.initialized:
                return False
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "comment": "Claude AI Trade"
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Ordre échoué {symbol}: {result.comment}")
                return False
            
            logger.info(f"✅ Ordre {symbol} placé - Ticket: {result.order}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur placement ordre: {e}")
            return False

# Classe Trading212
class Trading212Handler:
    def __init__(self):
        self.driver = None
        self.logged_in = False
        self.connect()
    
    def connect(self):
        """Connexion à Trading212 via Selenium"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            self.driver = webdriver.Chrome(options=options)
            
            self.driver.get("https://www.trading212.com/login")
            
            # Login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            self.driver.find_element(By.ID, "email").send_keys(TRADING212_EMAIL)
            self.driver.find_element(By.ID, "password").send_keys(TRADING212_PASSWORD)
            self.driver.find_element(By.ID, "loginBtn").click()
            
            time.sleep(3)
            self.logged_in = True
            logger.info("✅ Trading212 connecté (Selenium)")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erreur connexion Trading212: {e}")
            return False
    
    def place_order(self, symbol, direction, quantity):
        """Place un ordre Trading212"""
        try:
            if not self.logged_in:
                return False
            
            # Navigation et placement (exemple simplifié)
            self.driver.get(f"https://www.trading212.com/instruments/{symbol}")
            
            if direction == "BUY":
                self.driver.find_element(By.CLASS_NAME, "buy-btn").click()
            else:
                self.driver.find_element(By.CLASS_NAME, "sell-btn").click()
            
            logger.info(f"✅ Ordre Trading212 {symbol} {direction} placé")
            return True
        
        except Exception as e:
            logger.error(f"Erreur Trading212: {e}")
            return False

# Classe Indicateurs
class TechnicalAnalysis:
    @staticmethod
    def calculate_rsi(closes, period=14):
        """RSI"""
        try:
            rsi = RSI(closes.values, timeperiod=period)
            return rsi[-1] if not np.isnan(rsi[-1]) else None
        except:
            return None
    
    @staticmethod
    def calculate_macd(closes):
        """MACD"""
        try:
            macd, signal, hist = MACD(closes.values, fastperiod=12, slowperiod=26, signalperiod=9)
            return {
                "macd": macd[-1],
                "signal": signal[-1],
                "histogram": hist[-1]
            }
        except:
            return None
    
    @staticmethod
    def calculate_fibo(high, low):
        """Fibonacci Retracements"""
        range_val = high - low
        return {
            "0.236": high - (range_val * 0.236),
            "0.382": high - (range_val * 0.382),
            "0.5": high - (range_val * 0.5),
            "0.618": high - (range_val * 0.618)
        }
    
    @staticmethod
    def detect_order_blocks(df):
        """Détecte les Order Blocks (zones fortes)"""
        try:
            # Simplifié: cherche les zones de consolidation
            volatility = df['close'].pct_change().std()
            if volatility < df['close'].pct_change().mean() * 0.5:
                return {"ob_detected": True, "strength": "medium"}
            return {"ob_detected": False}
        except:
            return None
    
    @staticmethod
    def detect_fvg(df):
        """Fair Value Gap - écarts non comblés"""
        try:
            fvg_list = []
            for i in range(1, len(df) - 1):
                if df.iloc[i]['low'] > df.iloc[i-1]['high']:
                    fvg_list.append({
                        "type": "bullish",
                        "level": (df.iloc[i-1]['high'] + df.iloc[i]['low']) / 2
                    })
            return fvg_list
        except:
            return None
    
    @staticmethod
    def get_dxy():
        """Dollar Index - récupère DXY depuis une API"""
        try:
            # Appel API pour DXY (exemple avec une source gratuite)
            url = "https://api.example.com/dxy"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json().get("value")
            return None
        except:
            return None

# Classe Claude AI
class ClaudeDecisionMaker:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    def analyze_and_decide(self, symbol, indicators):
        """Claude décide BUY/SELL/HOLD"""
        try:
            prompt = f"""
Tu es un expert trader autonome. Analyse ces indicateurs pour {symbol}:

RSI: {indicators.get('rsi')}
MACD: {indicators.get('macd')}
Order Blocks: {indicators.get('ob')}
Fair Value Gap: {indicators.get('fvg')}
DXY (Force $): {indicators.get('dxy')}
Fibonacci Levels: {indicators.get('fibo')}

DECISION REQUISE:
1. BUY / SELL / HOLD ?
2. Confiance (0-100%): ?
3. Raison courte (1 phrase):

Format réponse:
ACTION: BUY/SELL/HOLD
CONFIDENCE: XX%
REASON: ...
"""
            
            message = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            logger.info(f"Claude décision pour {symbol}:\n{response_text}")
            
            # Parse réponse
            lines = response_text.split('\n')
            decision = {
                "action": "HOLD",
                "confidence": 0,
                "reason": ""
            }
            
            for line in lines:
                if "ACTION:" in line:
                    decision["action"] = line.split(":")[-1].strip()
                elif "CONFIDENCE:" in line:
                    try:
                        decision["confidence"] = int(line.split(":")[-1].replace("%", "").strip())
                    except:
                        pass
                elif "REASON:" in line:
                    decision["reason"] = line.split(":")[-1].strip()
            
            return decision
        
        except Exception as e:
            logger.error(f"Erreur Claude: {e}")
            return {"action": "HOLD", "confidence": 0, "reason": "Error"}

# Boucle principale
def main_trading_loop():
    logger.info("🚀 BOT TRADING DÉMARRE - RSI/MACD/OB/FVG/DXY/FIBO")
    
    mt4 = MT4Handler()
    t212 = Trading212Handler()
    ta = TechnicalAnalysis()
    claude = ClaudeDecisionMaker()
    
    while True:
        try:
            logger.info(f"⏰ Scan marché - {datetime.now()}")
            
            for symbol in SYMBOLS:
                logger.info(f"\n📊 Analyse {symbol}...")
                
                # Récupère les données
                df = mt4.get_candles(symbol, timeframe_minutes=240)
                if df is None or len(df) < 30:
                    continue
                
                # Calcule les indicateurs
                rsi = ta.calculate_rsi(df['close'])
                macd_data = ta.calculate_macd(df['close'])
                fibo = ta.calculate_fibo(df['high'].max(), df['low'].min())
                ob = ta.detect_order_blocks(df)
                fvg = ta.detect_fvg(df)
                dxy = ta.get_dxy()
                
                indicators = {
                    "rsi": f"{rsi:.2f}" if rsi else "N/A",
                    "macd": f"{macd_data['histogram']:.6f}" if macd_data else "N/A",
                    "fibo": fibo,
                    "ob": ob,
                    "fvg": len(fvg) if fvg else 0,
                    "dxy": dxy
                }
                
                # Claude décide
                decision = claude.analyze_and_decide(symbol, indicators)
                
                current_price = df['close'].iloc[-1]
                sl_price = current_price - (STOP_LOSS_PIPS * 0.0001)
                tp_price = current_price + (TAKE_PROFIT_PIPS * 0.0001)
                
                # Exécute les ordres
                if decision["action"] == "BUY" and decision["confidence"] > 60:
                    logger.info(f"🟢 BUY {symbol} @ {current_price} (Confiance: {decision['confidence']}%)")
                    mt4.place_order(symbol, mt5.ORDER_TYPE_BUY, LOT_SIZE, current_price, sl_price, tp_price)
                    t212.place_order(symbol, "BUY", LOT_SIZE)
                
                elif decision["action"] == "SELL" and decision["confidence"] > 60:
                    logger.info(f"🔴 SELL {symbol} @ {current_price} (Confiance: {decision['confidence']}%)")
                    mt4.place_order(symbol, mt5.ORDER_TYPE_SELL, LOT_SIZE, current_price, sl_price, tp_price)
                    t212.place_order(symbol, "SELL", LOT_SIZE)
                
                else:
                    logger.info(f"⚪ HOLD {symbol}")
            
            logger.info(f"✅ Scan terminé. Prochaine vérification dans {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)
        
        except Exception as e:
            logger.error(f"❌ Erreur boucle: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main_trading_loop()
