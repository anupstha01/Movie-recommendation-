# 🎬 Movie Recommendation System

This is an **AI-powered Movie Recommendation System** built using **Streamlit**.  
It suggests movies similar to a selected movie using **content-based filtering with cosine similarity**.  

The system is trained on the **TMDB 5000 Movies dataset** and fetches posters/details from the **TMDB API**.

---

## 📌 Features
- Search for movies from the dataset
- Get **Top-N recommendations**
- Display results as **cards with posters**
- View **analytics** (average, highest, lowest similarity score)
- Export recommendations as **CSV**
- Clean, responsive UI with sidebar controls

---

---

## ⚡ Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/anupstha01/Movie-recommendation-.git
````

### 2️⃣ Create and activate a virtual environment (recommended)

```bash
python -m venv venv
# Activate
venv\Scripts\activate      # On Windows
source venv/bin/activate   # On Mac/Linux
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Generate required files

Since **`similarity.pkl` is not uploaded**, you must generate both `movie_list.pkl` and `similarity.pkl` by running:

```bash
jupyter notebook movie_recomendation_system.ipynb
```

This will:

* Load the **TMDB 5000 dataset**
* Process the data
* Save `movie_list.pkl` and `similarity.pkl`

### 5️⃣ Run the Streamlit app

```bash
streamlit run app.py
```

---

## 🎥 Screenshots

### Homepage

![App Screenshot 1](Screenshot%20\(102\).png)

### Recommendations

![App Screenshot 2](Screenshot%20\(103\).png)

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **Pandas, NumPy, sklearn**
* **Pickle**
* **Requests (TMDB API)**

---

## 👨‍💻 Author

**Anup Shrestha**
🔗 [GitHub](https://github.com/anupstha01)

```
