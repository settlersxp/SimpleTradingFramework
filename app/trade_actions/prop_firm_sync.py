from typing import Dict, List, Optional
from datetime import datetime
import logging
from .mt5_client import MT5Client
from app.models.prop_firm import PropFirm
from app.models.trade import Trade
from app import db

logger = logging.getLogger(__name__)

class PropFirmSyncService:
    @staticmethod
    def sync_prop_firm(prop_firm: PropFirm) -> bool:
        """
        Synchronize prop firm information with MT5.
        Updates account information and creates new trades.
        """
        try:
            with MT5Client(
                username=prop_firm.username,
                password=prop_firm.password,
                server=prop_firm.ip_address,
                port=prop_firm.port
            ) as mt5_client:
                # Get account information
                account_info = mt5_client.get_account_info()
                if account_info:
                    # Update prop firm information
                    prop_firm.full_balance = account_info['balance']
                    prop_firm.available_balance = account_info['free_margin']
                    
                    # Calculate drawdown percentage
                    if account_info['balance'] > 0:
                        drawdown = ((account_info['balance'] - account_info['equity']) / account_info['balance']) * 100
                        prop_firm.dowdown_percentage = max(0, drawdown)
                    
                    # Get open positions
                    positions = mt5_client.get_open_positions()
                    if positions:
                        for position in positions:
                            # Check if trade already exists
                            existing_trade = Trade.query.filter_by(
                                platform_id=str(position['ticket']),
                                prop_firm_id=prop_firm.id
                            ).first()
                            
                            if not existing_trade:
                                # Create new trade
                                new_trade = Trade(
                                    prop_firm_id=prop_firm.id,
                                    platform_id=str(position['ticket']),
                                    strategy='MT5_SYNC',  # or extract from position comment
                                    order_type=position['type'],
                                    contracts=position['volume'],
                                    ticker=position['symbol'],
                                    position_size=abs(position['profit'] + position['swap']),
                                    created_at=datetime.fromisoformat(position['time']),
                                    response='Synced from MT5'
                                )
                                db.session.add(new_trade)
                    
                    # Commit all changes
                    db.session.commit()
                    return True
                
                return False
        except Exception as e:
            logger.error(f"Error syncing prop firm {prop_firm.id}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def sync_all_prop_firms() -> Dict[int, bool]:
        """
        Synchronize all active prop firms with MT5.
        Returns a dictionary of prop firm IDs and their sync status.
        """
        results = {}
        prop_firms = PropFirm.query.filter_by(is_active=True).all()
        
        for prop_firm in prop_firms:
            results[prop_firm.id] = PropFirmSyncService.sync_prop_firm(prop_firm)
        
        return results 