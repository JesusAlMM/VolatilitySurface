# **Volatility Surface Visualization App**

This repository contains an interactive **Volatility Surface Visualization App**, designed to compute and visualize the implied volatility surface of options using the **Black-Scholes model**. The application allows users to explore the volatility structure across different strike prices and expiration dates dynamically. Additionally, it provides tools for analyzing **option Greeks** and tracking historical volatility surfaces over time.  

🔗 https://volatilitysurf.streamlit.app/ 

## 📌 **Features**  

### **1. Volatility Surface Calculation**  
- Generates a **3D volatility surface** based on the Black-Scholes model.  
- Displays how implied volatility changes across **strike prices** and **time to expiration**.  

### **2. Greeks Calculation**  
- Click anywhere on the volatility surface to calculate key **Greeks**:  
  - **Delta** (sensitivity to price changes)  
  - **Gamma** (rate of change of Delta)  
  - **Vega** (sensitivity to volatility changes)  
  - **Theta** (time decay effect)  
  - **Rho** (sensitivity to interest rate changes)  
- Selected values, including **strike price** and **implied volatility**, are displayed in real time.  

### **3. Volatility Surface Gallery**  
- Users can **save volatility surfaces** at different time intervals (**30 min, 1 hour, 1 day, etc.**) to analyze changes over time.  
- The stored surfaces can be revisited in a historical visualization section.  

### **4. Customizable Parameters**  
- Adjust key inputs such as:  
  - **Spot price**  
  - **Strike price**  
  - **Volatility**  
  - **Time to maturity**  
  - **Risk-free rate**  
- The app dynamically updates all calculations based on user inputs.  


