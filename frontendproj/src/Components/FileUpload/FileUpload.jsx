import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [month, setMonth] = useState('');
  const [year, setYear] = useState('');
  const [message, setMessage] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleMonthChange = (e) => {
    setMonth(e.target.value);
  };

  const handleYearChange = (e) => {
    setYear(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !month || !year) {
      setMessage("Please select a file and specify month and year.");
      return;
    }

    setUploading(true);
    setMessage("");

    const formData = new FormData();
    const newFileName = `${month}-${year}-${file.name}`;
    const renamedFile = new File([file], newFileName, { type: file.type });
    formData.append("file", renamedFile);
    formData.append("month", month);
    formData.append("year", year);

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
      <h2>Upload Monthly Statement</h2>
      <form className="file-upload-form" onSubmit={handleSubmit}>
        <input type="file" className="file-input" onChange={handleFileChange} />
        <div className="file-upload-group">
          <label htmlFor="month" className="file-upload-label">Month</label>
          <select id="month" value={month} onChange={handleMonthChange} className="file-upload-select">
            <option value="">Select month</option>
            {["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].map((m) => (
              <option key={m} value={m.toLowerCase()}>{m}</option>
            ))}
          </select>
        </div>
        <div className="file-upload-group">
          <label htmlFor="year" className="file-upload-label">Year</label>
          <select id="year" value={year} onChange={handleYearChange} className="file-upload-select">
            <option value="">Select year</option>
            {Array.from({ length: 50 }, (_, i) => new Date().getFullYear() - i).map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
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

export default FileUpload;