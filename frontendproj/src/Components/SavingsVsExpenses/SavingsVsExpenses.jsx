import './SavingsVsExpenses.css';
import React, { useState } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js'; // Using Plotly for the bar chart

const SavingsVsExpenses = () => {
  const [month, setMonth] = useState('');
  const [year, setYear] = useState('');
  const [barGraphData, setBarGraphData] = useState(null);
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
      // Fetch bar graph data for the selected month and year
      const response = await axios.get(`http://localhost:8000/get_bar_graph_data/?month=${month}&year=${year}`);

      // Log the response data to inspect its structure
      console.log("Response data:", response.data);

      // If data is available, update barGraphData with the response data
      setBarGraphData(response.data);
      setMessage("");  // Clear any existing message
    } catch (error) {
      setBarGraphData(null);
      setMessage("No data found for the selected month and year.");
      console.error(error);
    }
  };

  return (
    <div className="categorize-transaction-container">
      <h2>Savings vs. Expenses</h2>
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
      <button onClick={handleSubmit} className="upload-transaction-button">Get Bar Graph Data</button>

      {message && <p>{message}</p>}

      {barGraphData && (
        <div>
          <h3>Savings vs. Expenses ({barGraphData.month_name})</h3>
          <Plot
            data={[{
              type: 'bar',
              x: barGraphData.weekly_spending.map(item => item.Week),
              y: barGraphData.weekly_spending.map(item => item.Amount),
              text: barGraphData.weekly_spending.map(item => item.Type),
              hoverinfo: 'x+y+text',
              marker: {
                color: barGraphData.weekly_spending.map(item => item.Type === 'Savings' ? 'green' : 'red'),
              },
            }]}
            layout={{
              title: 'Savings vs. Expenses',
              barmode: 'stack',
              xaxis: { title: 'Week of the Month' },
              yaxis: { title: 'Amount (₹)' },
              height: 400,
              width: 600,
            }}
          />
        </div>
      )}
    </div>
  );
};

export default SavingsVsExpenses;