import sqlite3

class DatabaseManager:
    def __init__(self, db_name="vikings.db"):
        self.db_name = db_name
        self.init_tables()

    def init_tables(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_name TEXT,
                    rarity TEXT,
                    FOREIGN KEY(user_id) REFERENCES players(user_id)
                )
            """)
            conn.commit()

    def get_player_data(self, user_id):
        """Récupère (XP, Niveau) d'un joueur."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT xp, level FROM players WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def add_xp(self, user_id, amount):
        """Ajoute de l'XP et gère le niveau."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (user_id,))
            
            cursor.execute("UPDATE players SET xp = xp + ? WHERE user_id = ?", (amount, user_id))
            
            cursor.execute("SELECT xp, level FROM players WHERE user_id = ?", (user_id,))
            xp, level = cursor.fetchone()
            
            next_level_xp = level * 100
            if xp >= next_level_xp:
                new_level = level + 1
                cursor.execute("UPDATE players SET level = ?, xp = ? WHERE user_id = ?", (new_level, xp - next_level_xp, user_id))
                conn.commit()
                return True, new_level 
            
            conn.commit()
            return False, level

    def add_item(self, user_id, item_name, rarity):
        """Ajoute un objet dans l'inventaire."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (user_id,))
            cursor.execute("INSERT INTO inventory (user_id, item_name, rarity) VALUES (?, ?, ?)", (user_id, item_name, rarity))
            conn.commit()

    def get_inventory(self, user_id):
        """Récupère la liste des objets."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT item_name, rarity FROM inventory WHERE user_id = ?", (user_id,))
            return cursor.fetchall()

    def get_top_players(self, limit=5):
        """Récupère les meilleurs joueurs pour le classement."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, level, xp FROM players ORDER BY level DESC, xp DESC LIMIT ?", (limit,))
            return cursor.fetchall()

    def remove_item(self, user_id, item_name):
        """Supprime un objet spécifique (pour l'offrande)."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ? LIMIT 1", (user_id, item_name))
            row = cursor.fetchone()
            
            if row:
                item_id = row[0]
                cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
                conn.commit()
                return True
            return False
    
    
        
        