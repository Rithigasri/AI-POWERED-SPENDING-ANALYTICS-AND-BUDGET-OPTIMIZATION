import React, { useState } from 'react';
import axios from 'axios';
import './OCRFunction.css';

const OCRFunction = () => {
  const [file, setFile] = useState(null);
  const [transactionType, setTransactionType] = useState('');
  const [message, setMessage] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTransactionTypeChange = (e) => {
    setTransactionType(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !transactionType) {
      setMessage("Please select a file and specify the transaction type.");
      return;
    }

    setUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("transactionType", transactionType);

    try {
      const response = await axios.post("http://localhost:8000/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setMessage("File uploaded successfully.");
    } catch (error) {
      console.error("Error uploading file:", error);
      setMessage("Error uploading file.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <h1>Upload Receipts</h1>
      <form className="file-upload-form" onSubmit={handleSubmit}>
        <input type="file" className="file-input" onChange={handleFileChange} />
        
        {/* Dropdown for Transaction Type */}
        <div className="file-upload-group">
          <label htmlFor="transactionType" className="file-upload-label">Transaction Type</label>
          <select 
            id="transactionType" 
            value={transactionType} 
            onChange={handleTransactionTypeChange} 
            className="file-upload-select"
          >
            <option value="">Select Transaction Type</option>
            <option value="received">Received</option>
            <option value="paid">Paid</option>
          </select>
        </div>

        <button type="submit" className="upload-button" disabled={uploading}>
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {message && <div className="status-message">{message}</div>}
    </div>
  );
};

export default OCRFunction;
