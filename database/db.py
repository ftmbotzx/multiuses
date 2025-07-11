import motor.motor_asyncio
from datetime import datetime, timedelta
from info import Config


class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_NAME]
        self._connected = False

        # Collections
        self.users = self.db["users"]
        self.operations = self.db["operations"]
        self.premium_codes = self.db["premium_codes"]
        self.referrals = self.db["referrals"]

    async def connect(self):
        """Connect to the database and create indexes"""
        try:
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            # Create indexes
            await self.create_indexes()
            print("Database connected successfully")
        except Exception as e:
            print(f"Database connection failed: {e}")
            self._connected = False

    async def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()
            self._connected = False

    async def create_indexes(self):
        await self.users.create_index("user_id", unique=True)
        await self.users.create_index("referral_code", unique=True)
        await self.users.create_index("referred_by")

        await self.operations.create_index([("user_id", 1), ("date", -1)])
        await self.operations.create_index("date", expireAfterSeconds=86400 * 30)

        await self.premium_codes.create_index("code", unique=True)
        await self.premium_codes.create_index("used")

        await self.referrals.create_index("referrer_id")
        await self.referrals.create_index("referred_id")

    async def get_user(self, user_id: int):
        return await self.users.find_one({"user_id": user_id})

    async def create_user(self, user_id: int, username: str = None, first_name: str = None, referred_by: int = None):
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "credits": Config.DEFAULT_CREDITS,
            "premium_until": None,
            "banned": False,
            "daily_usage": 0,
            "last_usage_reset": datetime.now(),
            "referral_code": f"ref_{user_id}",
            "referred_by": referred_by,
            "total_operations": 0,
            "joined_date": datetime.now(),
            "last_activity": datetime.now()
        }

        result = await self.users.insert_one(user_data)

        if referred_by:
            await self.handle_referral(referred_by, user_id)

        return result.inserted_id

    async def update_user(self, user_id: int, update_data: dict):
        update_data["last_activity"] = datetime.now()
        return await self.users.update_one({"user_id": user_id}, {"$set": update_data})

    async def add_credits(self, user_id: int, amount: int):
        return await self.users.update_one({"user_id": user_id}, {"$inc": {"credits": amount}})

    async def deduct_credits(self, user_id: int, amount: int):
        user = await self.get_user(user_id)
        if not user or user["credits"] < amount:
            return False
        await self.users.update_one({"user_id": user_id}, {"$inc": {"credits": -amount}})
        return True

    async def reset_daily_usage(self, user_id: int):
        return await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"daily_usage": 0, "last_usage_reset": datetime.now()}}
        )

    async def check_daily_limit(self, user_id: int):
        user = await self.get_user(user_id)
        if not user:
            return False

        premium_until = user.get("premium_until") or datetime.now()
        if premium_until > datetime.now():
            return True

        last_reset = user.get("last_usage_reset") or datetime.now()
        if (datetime.now() - last_reset).days >= 1:
            await self.reset_daily_usage(user_id)
            return True

        return user.get("daily_usage", 0) < Config.DAILY_LIMIT

    async def increment_daily_usage(self, user_id: int):
        return await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"daily_usage": 1, "total_operations": 1}}
        )

    async def handle_referral(self, referrer_id: int, referred_id: int):
        existing = await self.referrals.find_one({
            "referrer_id": referrer_id,
            "referred_id": referred_id
        })

        if not existing:
            await self.referrals.insert_one({
                "referrer_id": referrer_id,
                "referred_id": referred_id,
                "date": datetime.now(),
                "bonus_given": True
            })
            await self.add_credits(referrer_id, Config.REFERRAL_BONUS)
            return True
        return False

    async def get_referral_stats(self, user_id: int):
        return await self.referrals.count_documents({"referrer_id": user_id})

    async def add_operation(self, user_id: int, operation_type: str, status: str = "pending"):
        return await self.operations.insert_one({
            "user_id": user_id,
            "operation_type": operation_type,
            "status": status,
            "date": datetime.now(),
            "credits_used": Config.PROCESS_COST
        })

    async def update_operation(self, operation_id, update_data: dict):
        return await self.operations.update_one({"_id": operation_id}, {"$set": update_data})

    async def create_premium_code(self, code: str, days: int, created_by: int):
        return await self.premium_codes.insert_one({
            "code": code,
            "days": days,
            "created_by": created_by,
            "created_date": datetime.now(),
            "used": False,
            "used_by": None,
            "used_date": None
        })

    async def redeem_premium_code(self, code: str, user_id: int):
        premium_code = await self.premium_codes.find_one({"code": code, "used": False})
        if not premium_code:
            return False

        await self.premium_codes.update_one(
            {"code": code},
            {"$set": {"used": True, "used_by": user_id, "used_date": datetime.now()}}
        )

        user = await self.get_user(user_id)
        current_premium = user.get("premium_until") or datetime.now()
        if current_premium < datetime.now():
            current_premium = datetime.now()

        new_premium_until = current_premium + timedelta(days=premium_code["days"])
        await self.update_user(user_id, {"premium_until": new_premium_until})
        return premium_code["days"]

    async def get_user_stats(self):
        total_users = await self.users.count_documents({})
        active_users = await self.users.count_documents({
            "last_activity": {"$gte": datetime.now() - timedelta(days=7)}
        })
        premium_users = await self.users.count_documents({
            "premium_until": {"$gt": datetime.now()}
        })
        return {
            "total_users": total_users,
            "active_users": active_users,
            "premium_users": premium_users
        }

    async def ban_user(self, user_id: int):
        return await self.update_user(user_id, {"banned": True})

    async def unban_user(self, user_id: int):
        return await self.update_user(user_id, {"banned": False})

    async def is_user_banned(self, user_id: int):
        user = await self.get_user(user_id)
        return user and user.get("banned", False)

    async def is_user_premium(self, user_id: int):
        user = await self.get_user(user_id)
        if not user:
            return False
        premium_until = user.get("premium_until") or datetime.now()
        return premium_until > datetime.now()

    async def add_premium_time(self, user_id: int, days: int):
        user = await self.get_user(user_id)
        if not user:
            return False
        current_premium = user.get("premium_until") or datetime.now()
        if current_premium < datetime.now():
            current_premium = datetime.now()

        new_premium_until = current_premium + timedelta(days=days)
        await self.update_user(user_id, {"premium_until": new_premium_until})
        return True


db = Database()