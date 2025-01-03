# Don't Break The Chain
**Do something new every day**

---

This project is a Flask application that allows users to manage and track daily chains (e.g., habit streaks). It includes features such as error handling, database-backed chain management, and a statistics dashboard.

## **Features**

- Manage habit chains with CRUD operations.
- View daily calendar and track completed days.
- Statistics for each chain: current streak, longest streak, and percentage of marked days in the current year.
- Robust error handling for common HTTP errors (404, 500, etc.).
- JSON and HTML responses based on client preferences.

## **Installation**

### **1. Clone the Repository**
```
git clone <repository_url>
cd <repository_name>
```

### **2. Create a Virtual Environment**
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```
pip install flask flask_sqlalchemy
```

## **Usage**

### **1. Running the Application**

Run the application using:
```
python3 app.py
```

The app will be accessible at `http://127.0.0.1:5000`.

## **Application Structure**

### **Main Files**

- **`app.py`**: Main Flask application.
- **`errors.py`**: Handles all HTTP error responses.
- **`templates/`**: Contains HTML templates for pages and error views.
* * *

## **API Endpoints**

### **Habit Chain Management**

| Endpoint | Method | Description | 
| ---- | ---- | ----  |
| `/` | GET | Home page with a daily calendar. | 
| `/get_chains` | GET | Retrieve all available chains. | 
| `/add_chain` | POST | Add a new chain. | 
| `/delete_chain` | POST | Delete a specific chain and its data. | 
| `/mark_date` | POST | Mark/unmark a specific date for a chain. | 
| `/get_dates` | GET | Retrieve all marked dates for a specific chain. | 
| `/get_calendar` | GET | Retrieve the calendar structure. | 
| `/chain_stats` | GET | Retrieve statistics for a specific chain. | 
| `/view_stats` | GET | View the statistics page. | 

## **Error Handling**

The app includes a robust error-handling mechanism.

### **Errors Handled**

| Error Code | Description | Template | 
| ---- | ---- | ----  |
| 404 | Page not found. | `404.html` | 
| 500 | Internal server error. | `500.html` | 
| 403 | Forbidden access. | `403.html` | 
| 400 | Bad request. | `400.html` | 
| Generic | Handles other unexpected errors. | `generic.html` | 

### **Testing Error Routes**

- **404 Error**: Visit a non-existent route (e.g., `/nonexistent`).
- **500 Error**: Raise an intentional error in a route:
```
@app.route('/trigger-500')
def trigger_500():
    raise Exception("Simulated 500 error")
```

- **403 Error**: Trigger forbidden access:
```
@app.route('/trigger-403')
def trigger_403():
    abort(403)
```

## **Database Schema**

### **Models**

1. **`Chain`**

    - `id`: Unique ID for the chain.
    - `name`: Name of the chain (unique).
2. **`ChainDate`**

    - `id`: Unique ID for the date.
    - `date`: Date marked in the chain (`YYYY-MM-DD` format).
    - `chain_name`: Associated chain name.

## **Customization**

### **Adding New Features**

- Add more routes for advanced chain management.
- Include additional error handlers for other HTTP statuses.
- Integrate user authentication or multi-user support.

### **Styling**

- Modify `templates/` for custom styles.
- Use TailwindCSS (already included) for rapid UI development.

## **Contributing**

Feel free to submit issues or pull requests. Contributions are welcome!

## **License**

This project is open-source and available under the MIT License.