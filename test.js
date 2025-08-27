document.addEventListener('DOMContentLoaded', function() {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // Clear the "Loading..." message

    // --- Test Cases ---
    const testFakeNews = {
        headline: "SHOCKING: Scientists discover miracle cure that doctors don't want you to know about",
        content: "This incredible breakthrough will change everything. The government is hiding this secret treatment that can cure all diseases overnight. You won't believe what happens next!"
    };
    
    const testRealNews = {
        headline: "Local community center opens new facility",
        content: "The community center has completed construction of its new recreation facility. The building includes a gymnasium, swimming pool, and meeting rooms for local residents."
    };
    
    /**
     * A function to call the API and display the results on the test page.
     * @param {Object} news - The news object with headline and content.
     * @param {string} type - A string descriptor for the test type (e.g., 'Fake').
     */
    async function testApiCall(news, type) {
        const formData = new FormData();
        formData.append('headline', news.headline);
        formData.append('content', news.content);
        
        const resultDiv = document.createElement('div');
        resultDiv.classList.add('result');
        resultDiv.innerHTML = `<h3>Testing ${type} News...</h3>`;
        resultsContainer.appendChild(resultDiv);

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Style the result div based on the prediction
            resultDiv.classList.add(result.prediction.toLowerCase());
            resultDiv.innerHTML = `
                <h3>${type} News Test: PASSED</h3>
                <p><strong>Prediction:</strong> ${result.prediction}</p>
                <p><strong>Confidence:</strong> ${result.confidence}</p>
            `;
            
        } catch (error) {
            resultDiv.classList.add('fake'); // Style as an error
            resultDiv.innerHTML = `<h3>Testing ${type} News: FAILED</h3><p><strong>Error:</strong> ${error.message}</p>`;
        }
    }
    
    // Run the tests sequentially.
    async function runTests() {
        await testApiCall(testFakeNews, 'Fake');
        await testApiCall(testRealNews, 'Real');
    }

    runTests();
});