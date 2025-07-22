"""
Stock Pick Performance Tracker
==============================

Track the performance of individual stock picks from your trading system
to analyze which signals work best and improve your strategy.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.WARNING)

class PickTracker:
    """Track performance of individual stock picks."""
    
    def __init__(self):
        self.picks_file = "stock_picks_history.json"
        self.performance_file = "pick_performance.csv"
        
    def add_pick(self, symbol: str, entry_price: float, stop_loss: float, 
                take_profit: float, signals: list, confidence: float):
        """Add a new stock pick to tracking."""
        
        pick_data = {
            'symbol': symbol,
            'pick_date': datetime.now().isoformat(),
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'signals': signals,
            'confidence': confidence,
            'status': 'ACTIVE',
            'exit_price': None,
            'exit_date': None,
            'pnl_pct': None,
            'outcome': None
        }
        
        # Load existing picks
        picks = self._load_picks()
        picks.append(pick_data)
        
        # Save updated picks
        self._save_picks(picks)
        
        print(f"✅ Added pick: {symbol} at ₹{entry_price:.2f}")
    
    def update_pick_performance(self):
        """Update performance of all active picks."""
        
        picks = self._load_picks()
        if not picks:
            print("No picks to update.")
            return
        
        try:
            from trading_system.data_manager import DataManager
            from trading_system.config import TradingConfig
            
            config = TradingConfig()
            data_manager = DataManager(config)
            
            updates = 0
            
            for pick in picks:
                if pick['status'] != 'ACTIVE':
                    continue
                
                try:
                    # Get current price
                    symbol = pick['symbol']
                    current_data = data_manager.get_stock_data(symbol, period='5d')
                    
                    if current_data is None or len(current_data) == 0:
                        continue
                    
                    current_price = current_data['close'].iloc[-1]
                    entry_price = pick['entry_price']
                    stop_loss = pick['stop_loss']
                    take_profit = pick['take_profit']
                    
                    # Check if pick should be closed
                    if current_price <= stop_loss:
                        pick['status'] = 'CLOSED'
                        pick['exit_price'] = stop_loss
                        pick['exit_date'] = datetime.now().isoformat()
                        pick['pnl_pct'] = (stop_loss - entry_price) / entry_price * 100
                        pick['outcome'] = 'LOSS'
                        updates += 1
                        print(f"❌ {symbol}: Hit stop loss at ₹{stop_loss:.2f}")
                    
                    elif current_price >= take_profit:
                        pick['status'] = 'CLOSED'
                        pick['exit_price'] = take_profit
                        pick['exit_date'] = datetime.now().isoformat()
                        pick['pnl_pct'] = (take_profit - entry_price) / entry_price * 100
                        pick['outcome'] = 'WIN'
                        updates += 1
                        print(f"✅ {symbol}: Hit take profit at ₹{take_profit:.2f}")
                    
                    # Check if too old (close after 10 days)
                    pick_date = datetime.fromisoformat(pick['pick_date'])
                    if (datetime.now() - pick_date).days >= 10:
                        pick['status'] = 'CLOSED'
                        pick['exit_price'] = current_price
                        pick['exit_date'] = datetime.now().isoformat()
                        pick['pnl_pct'] = (current_price - entry_price) / entry_price * 100
                        pick['outcome'] = 'WIN' if current_price > entry_price else 'LOSS'
                        updates += 1
                        print(f"⏰ {symbol}: Closed after 10 days at ₹{current_price:.2f}")
                
                except Exception as e:
                    print(f"Error updating {pick.get('symbol', 'Unknown')}: {e}")
                    continue
            
            # Save updated picks
            self._save_picks(picks)
            
            if updates > 0:
                print(f"\n✅ Updated {updates} picks")
                self._generate_performance_report()
            else:
                print("No picks needed updating.")
        
        except Exception as e:
            print(f"Error updating picks: {e}")
    
    def _load_picks(self) -> list:
        """Load picks from file."""
        try:
            with open(self.picks_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading picks: {e}")
            return []
    
    def _save_picks(self, picks: list):
        """Save picks to file."""
        try:
            with open(self.picks_file, 'w') as f:
                json.dump(picks, f, indent=2)
        except Exception as e:
            print(f"Error saving picks: {e}")
    
    def _generate_performance_report(self):
        """Generate performance report."""
        picks = self._load_picks()
        
        if not picks:
            print("No picks available for report.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(picks)
        
        # Filter closed picks for analysis
        closed_picks = df[df['status'] == 'CLOSED'].copy()
        
        if len(closed_picks) == 0:
            print("No closed picks for performance analysis.")
            return
        
        # Calculate metrics
        total_picks = len(closed_picks)
        wins = len(closed_picks[closed_picks['outcome'] == 'WIN'])
        losses = len(closed_picks[closed_picks['outcome'] == 'LOSS'])
        win_rate = (wins / total_picks) * 100 if total_picks > 0 else 0
        
        avg_win = closed_picks[closed_picks['outcome'] == 'WIN']['pnl_pct'].mean() if wins > 0 else 0
        avg_loss = abs(closed_picks[closed_picks['outcome'] == 'LOSS']['pnl_pct'].mean()) if losses > 0 else 0
        
        best_pick = closed_picks.loc[closed_picks['pnl_pct'].idxmax()] if not closed_picks.empty else None
        worst_pick = closed_picks.loc[closed_picks['pnl_pct'].idxmin()] if not closed_picks.empty else None
        
        # Print report
        print(f"\n📊 STOCK PICKS PERFORMANCE REPORT")
        print("=" * 50)
        print(f"📈 Total Closed Picks: {total_picks}")
        print(f"✅ Winning Picks: {wins}")
        print(f"❌ Losing Picks: {losses}")
        print(f"🏆 Win Rate: {win_rate:.1f}%")
        
        if avg_win > 0:
            print(f"📈 Average Win: +{avg_win:.2f}%")
        if avg_loss > 0:
            print(f"📉 Average Loss: -{avg_loss:.2f}%")
        
        if best_pick is not None:
            print(f"🚀 Best Pick: {best_pick['symbol']} (+{best_pick['pnl_pct']:.2f}%)")
        if worst_pick is not None:
            print(f"💥 Worst Pick: {worst_pick['symbol']} ({worst_pick['pnl_pct']:.2f}%)")
        
        # Active picks
        active_picks = df[df['status'] == 'ACTIVE']
        if len(active_picks) > 0:
            print(f"\n🔄 Active Picks: {len(active_picks)}")
            for _, pick in active_picks.iterrows():
                print(f"   • {pick['symbol']}: ₹{pick['entry_price']:.2f}")
        
        # Save detailed report
        closed_picks.to_csv(self.performance_file, index=False)
        print(f"\n💾 Detailed report saved to: {self.performance_file}")


def track_todays_picks():
    """Track today's stock picks from analysis."""
    
    print("📊 STOCK PICK PERFORMANCE TRACKER")
    print("=" * 50)
    
    tracker = PickTracker()
    
    # Update existing picks first
    print("🔄 Updating existing picks...")
    tracker.update_pick_performance()
    
    # Option to add new picks
    print(f"\n➕ Add today's picks? (y/n): ", end="")
    response = input().lower()
    
    if response == 'y':
        print("\nRun your analysis first to get picks, then add them here:")
        print("python analyze_today.py")
        print("\nManual entry mode:")
        
        while True:
            print(f"\nEnter stock pick details (or 'done' to finish):")
            symbol = input("Symbol (e.g., RELIANCE.NS): ").strip()
            
            if symbol.lower() == 'done':
                break
            
            try:
                entry_price = float(input("Entry Price (₹): "))
                stop_loss = float(input("Stop Loss (₹): "))
                take_profit = float(input("Take Profit (₹): "))
                confidence = float(input("Confidence (0-1): "))
                signals = input("Key Signals (comma separated): ").split(',')
                
                tracker.add_pick(symbol, entry_price, stop_loss, take_profit, 
                               [s.strip() for s in signals], confidence)
            
            except ValueError:
                print("Invalid input. Please enter numeric values correctly.")
            except Exception as e:
                print(f"Error adding pick: {e}")


def main():
    """Main function."""
    try:
        track_todays_picks()
    except KeyboardInterrupt:
        print("\n\n⏹️ Pick tracking interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
