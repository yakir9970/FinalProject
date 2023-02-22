import React, { useState } from 'react';
import axios from 'axios';
import * as d3 from 'd3';

 

function App() {
    const [file1, setFile1] = useState(null);
    const [file2, setFile2] = useState(null);
    const [result, setResult] = useState(null);

 

    const handleFile1Change = (event) => {
        setFile1(event.target.files[0]);
    }

 

    const handleFile2Change = (event) => {
        setFile2(event.target.files[0]);
    }

 

    const handleSubmit = (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('file1', file1);
        formData.append('file2', file2);
        axios.post('/compare-xml', formData)
            .then(response => {
                setResult(response.data);
            })
            .catch(error => {
                console.error(error);
            });
    }

 

    // D3.js code to display the result
    // ...

 

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <label>
                    XML file 1:
                    <input type="file" onChange={handleFile1Change} />
                </label>
                <label>
                    XML file 2:
                    <input type="file" onChange={handleFile2Change} />
                </label>
                <button type="submit">Compare</button>
            </form>
            <div id="d3-visualization">
                {/* D3.js visualization */}
            </div>
        </div>
    );
}
export default App;