from datetime import datetime, timedelta
import random
from backend.extensions import db
from backend.models import MarketPrice, PriceWatchlist, User
from backend.services.notification_service import NotificationService
import google.generativeai as genai
import os

class MarketIntelligenceService:
    @staticmethod
    def get_market_prices(district=None, crop_name=None):
        query = MarketPrice.query
        if district:
            query = query.filter_by(district=district)
        if crop_name:
            query = query.filter_by(crop_name=crop_name)
        return query.all()

    @staticmethod
    def fetch_live_prices():
        """
        In a real scenario, this would call a govt API.
        For now, we simulate data ingestion/updates.
        """
        crops = ['Tomato', 'Onion', 'Wheat', 'Rice', 'Cotton']
        districts = ['Pune', 'Nashik', 'Nagpur', 'Mumbai', 'Aurangabad']
        
        updated_data = []
        for crop in crops:
            for district in districts:
                # Find existing or create new
                price_record = MarketPrice.query.filter_by(crop_name=crop, district=district).first()
                
                # Dynamic price simulation (+/- 5% movement)
                base_price = price_record.modal_price if price_record else random.randint(1000, 5000)
                change = base_price * random.uniform(-0.05, 0.05)
                new_price = round(base_price + change, 2)
                
                if not price_record:
                    price_record = MarketPrice(
                        crop_name=crop,
                        district=district,
                        state='Maharashtra',
                        modal_price=new_price,
                        min_price=new_price * 0.9,
                        max_price=new_price * 1.1,
                        unit='Quintal'
                    )
                    db.session.add(price_record)
                else:
                    price_record.modal_price = new_price
                    price_record.min_price = round(new_price * 0.9, 2)
                    price_record.max_price = round(new_price * 1.1, 2)
                
                updated_data.append(price_record.to_dict())
        
        db.session.commit()
        return updated_data

    @staticmethod
    def analyze_price_trends(crop_name, district):
        """
        Use Gemini AI to analyze price trends and give recommendations.
        """
        # Fetch historical context (simulated here with same random logic)
        current_price = MarketPrice.query.filter_by(crop_name=crop_name, district=district).first()
        if not current_price:
            return {"error": "No data found for this crop/district"}

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return {"error": "AI Service not configured"}

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        Analyze the market trend for {crop_name} in {district}.
        Current Price: ₹{current_price.modal_price} per {current_price.unit}.
        
        Recent Context: Prices have seen a 12% increase in the last 2 weeks due to unseasonal rains affecting supply chains.
        
        Provide:
        1. Trend Analysis (Short term)
        2. Recommendation: "SELL NOW" or "HOLD"
        3. Simple Reasoning for farmers.
        Keep it concise and supportive.
        """

        try:
            response = model.generate_content(prompt)
            return {
                "crop": crop_name,
                "district": district,
                "analysis": response.text,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def check_watchlist_alerts(updated_prices):
        """
        Check if updated prices cross target thresholds for users.
        """
        alerts_triggered = []
        for price_data in updated_prices:
            watchers = PriceWatchlist.query.filter_by(
                crop_name=price_data['crop_name'], 
                alert_enabled=True
            ).all()
            
            for watcher in watchers:
                # Trigger alert if current price is higher than target (Profit opportunity)
                if price_data['modal_price'] >= watcher.target_price:
                    msg = f"Alert! {watcher.crop_name} price in {price_data['district']} reached ₹{price_data['modal_price']}, crossing your target of ₹{watcher.target_price}."
                    
                    NotificationService.create_notification(
                        user_id=watcher.user_id,
                        title="Market Price Alert",
                        message=msg,
                        notification_type="price_alert"
                    )
                    alerts_triggered.append({
                        "user_id": watcher.user_id,
                        "msg": msg
                    })
        return alerts_triggered
