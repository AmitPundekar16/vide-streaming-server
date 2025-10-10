# ---------- SearchBar.py ----------
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from difflib import get_close_matches

# Buckets in your system
BUCKETS = [
    "cricket", "fruits",  "movies",
    "music", "education", "news",    "games", "animals"
]

# Optional keyword mapping to auto-detect buckets from search terms
KEYWORDS = {
    "cricket": ["rohit", "virat", "ipl", "bat", "ball", "wicket", "match"],
    "fruits": ["apple", "banana", "mango", "grape", "orange"],
    "movies": ["actor", "film", "bollywood", "hollywood", "cinema"],
    "music": ["song", "album", "melody", "artist"],
    "games": ["pubg", "chess", "minecraft", "valorant"],
    "animals": ["dog", "cat", "lion", "tiger", "elephant"],
}


class SearchBar(QWidget):
    def __init__(self, parent=None, search_callback=None):
        super().__init__(parent)

        # --- UI Setup ---
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search videos or categories...")
        self.search_btn = QPushButton("Search")

        layout = QHBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.search_btn)
        self.setLayout(layout)

        # Callback function from main GUI
        self.search_callback = search_callback

        # Connect actions
        self.search_btn.clicked.connect(self.perform_search)
        self.search_bar.returnPressed.connect(self.perform_search)

    # ---------- Logic Section ----------

    def correct_word(self, word, choices):
        """Auto-correct misspelled words."""
        matches = get_close_matches(word.lower(), choices, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def find_bucket_by_keyword(self, query):
        """Match keywords to known buckets."""
        for bucket, words in KEYWORDS.items():
            for word in words:
                if word in query.lower():
                    return bucket
        return None

    def perform_search(self):
        """Handle search event and return bucket name."""
        query = self.search_bar.text().strip().lower()

        if not query:
            QMessageBox.warning(self, "Search", "Please enter something to search!")
            return None

        # Step 1: Try correcting the bucket name directly
        corrected_bucket = self.correct_word(query, BUCKETS)

        # Step 2: If not a bucket, try keyword mapping
        if not corrected_bucket:
            corrected_bucket = self.find_bucket_by_keyword(query)

        # Step 3: Handle results
        if corrected_bucket:
            # ✅ Return bucket name to parent
            if self.search_callback:
                self.search_callback(corrected_bucket)
            return corrected_bucket
        else:
            QMessageBox.information(self, "Search", "Oops! No video found 😢")
            return None
