# **Volatility Surface Visualization App**

This repository contains an interactive **Volatility Surface Visualization App**, designed to compute and visualize the implied volatility surface of options using the **Black-Scholes model**. The application allows users to explore the volatility structure across different strike prices and expiration dates dynamically. Additionally, it provides tools for analyzing **option Greeks** and tracking historical volatility surfaces over time.  

🔗 **Live Demo:** [Your Streamlit App URL]  

## 🚀 **Features**  

### 📈 **Volatility Surface Calculation**  
- Generates a **3D volatility surface** based on the Black-Scholes model.  
- Displays how implied volatility changes across **strike prices** and **time to expiration**.  
- Provides an interactive visualization using **Plotly**.  

### 📊 **Greeks Calculation**  
- Click anywhere on the volatility surface to calculate key **Greeks**:  
  - **Delta** (sensitivity to price changes)  
  - **Gamma** (rate of change of Delta)  
  - **Vega** (sensitivity to volatility changes)  
  - **Theta** (time decay effect)  
  - **Rho** (sensitivity to interest rate changes)  
- Selected values, including **strike price** and **implied volatility**, are displayed in real time.  

### 🖼 **Volatility Surface Gallery**  
- Users can **save volatility surfaces** at different time intervals (**30 min, 1 hour, 1 day, etc.**) to analyze changes over time.  
- The stored surfaces can be revisited in a historical visualization section.  
- Saves data in an **Excel file**, including input parameters and generated plots, instead of using local folders.  

### ⚙️ **Customizable Parameters**  
- Adjust key inputs such as:  
  - **Spot price**  
  - **Strike price**  
  - **Volatility**  
  - **Time to maturity**  
  - **Risk-free rate**  
- The app dynamically updates all calculations based on user inputs.  

## 🔧 **Dependencies**  
- **Streamlit** – Web-based interactive dashboard.  
- **Plotly** – High-quality 3D visualization.  
- **NumPy & Pandas** – Data processing and calculations.  
- **yFinance** (optional) – Fetches real-time market data.  

## 📌 **How to Run**  

1. Clone this repository:  
   ```bash
   git clone https://github.com/yourusername/your-repository.git




