import './CategorizeTransaction.css';
import React, { useState } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js'; // Using Plotly for the pie chart

const CategorizeTransaction = () => {
  const [month, setMonth] = useState('');
  const [year, setYear] = useState('');
  const [fileData, setFileData] = useState(null);
  const [message, setMessage] = useState('');

  const handleMonthChange = (e) => {
    setMonth(e.target.value);
  };

  const handleYearChange = (e) => {
    setYear(e.target.value);
  };

  const handleSubmit = async () => {
    if (!month || !year) {
      setMessage("Please specify the month and year.");
      return;
    }

    try {
      // Check if data exists for the selected month and year
      const response = await axios.get(`http://localhost:8000/get_graph_data/?month=${month}&year=${year}`);

      // If data is available, update fileData with graph data
      setFileData(response.data);
      setMessage("");  // Clear any existing message
    } catch (error) {
      setFileData(null);
      setMessage("No data found for the selected month and year.");
      console.error(error);
    }
  };
  
return (
    <div className="categorize-transaction-container">
        <h2>Categorize Transactions</h2>
        <div className="dropdown-container">
            <label className="dropdown-label">Month:</label>
            <select value={month} onChange={handleMonthChange} className="dropdown-select">
                <option value="">Select Month</option>
                {["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].map((m) => (
                    <option key={m} value={m.toLowerCase()}>{m}</option>
                ))}
            </select>
        </div>
        <div className="dropdown-container">
            <label className="dropdown-label">Year:</label>
            <select value={year} onChange={handleYearChange} className="dropdown-select">
                <option value="">Select Year</option>
                {Array.from({ length: 50 }, (_, i) => new Date().getFullYear() - i).map((y) => (
                    <option key={y} value={y}>{y}</option>
                ))}
            </select>
        </div>
        <button onClick={handleSubmit} className="upload-transaction-button">Categorize Transactions</button>

        {message && <p>{message}</p>}

        {fileData && (
            <div>
                <h3>Spending Breakdown by Category</h3>
                <Plot
                    data={[{
                        type: 'pie',
                        labels: fileData.map(item => item.Category),
                        values: fileData.map(item => item.Amount),
                        hoverinfo: 'label+percent',
                        textinfo: 'value',
                        marker: {
                            colors: ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#FFFF99', '#FFB3E6'],
                        },
                    }]}
                    layout={{
                        title: 'Spending Breakdown by Category',
                        height: 400,
                        width: 600,
                    }}
                />
            </div>
        )}
    </div>
);
  return (
    <div className="categorize-transaction-container">
      <h2>Categorize Transactions</h2>
      <div>
        <label>Month:</label>
        <select value={month} onChange={handleMonthChange}>
          <option value="">Select Month</option>
          {["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].map((m) => (
            <option key={m} value={m.toLowerCase()}>{m}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Year:</label>
        <select value={year} onChange={handleYearChange}>
          <option value="">Select Year</option>
          {Array.from({ length: 50 }, (_, i) => new Date().getFullYear() - i).map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>
      <button onClick={handleSubmit}>Categorize Transactions</button>

      {message && <p>{message}</p>}

      {fileData && (
        <div>
          <h3>Spending Breakdown by Category</h3>
          <Plot
            data={[{
              type: 'pie',
              labels: fileData.map(item => item.Category),
              values: fileData.map(item => item.Amount),
              hoverinfo: 'label+percent',
              textinfo: 'value',
              marker: {
                colors: ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#FFFF99', '#FFB3E6'],
              },
            }]}
            layout={{
              title: 'Spending Breakdown by Category',
              height: 400,
              width: 600,
            }}
          />
        </div>
      )}
    </div>
  );
};

export default CategorizeTransaction;
