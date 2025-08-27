// This event listener ensures that the script runs only after the entire HTML
// page has been loaded and is ready.
document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. DOM Element Selection ---
    // We get references to all the HTML elements we need to interact with.
    // This makes the code cleaner and faster.
    const newsForm = document.getElementById('news-form');
    const headlineInput = document.getElementById('headline');
    const contentInput = document.getElementById('content');
    const imageInput = document.getElementById('image');
    const fileNameDisplay = document.getElementById('file-name');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeImageButton = document.getElementById('remove-image');
    
    const inputSection = document.querySelector('.input-section');
    const resultsSection = document.getElementById('results-section');
    
    const predictionElement = document.getElementById('prediction');
    const confidenceMeter = document.getElementById('confidence-meter');
    const confidenceValue = document.getElementById('confidence-value');
    const explanationElement = document.getElementById('explanation');
    const relatedNewsContainer = document.getElementById('related-news-container');
    const factChecksContainer = document.getElementById('fact-checks-container');
    const loadingOverlay = document.getElementById('loading-overlay');
    const newAnalysisButton = document.getElementById('new-analysis');

    // The URL of our backend API.
    const API_URL = 'http://localhost:8000';

    // --- 2. Event Listeners ---
    // These functions "listen" for user actions like clicking a button or submitting a form.
    newsForm.addEventListener('submit', handleFormSubmit);
    imageInput.addEventListener('change', handleImageSelection);
    removeImageButton.addEventListener('click', removeSelectedImage);
    newAnalysisButton.addEventListener('click', resetForm);

    /**
     * Main function to handle the form submission when the "Analyze" button is clicked.
     * @param {Event} event - The form submission event.
     */
    async function handleFormSubmit(event) {
        event.preventDefault(); // Prevents the browser from reloading the page.
        
        // Prepare the data to be sent to the backend.
        const formData = new FormData();
        formData.append('headline', headlineInput.value.trim());
        formData.append('content', contentInput.value.trim());
        
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }
        
        // Show a loading spinner to the user.
        loadingOverlay.classList.remove('hidden');
        
        try {
            // Use the 'fetch' API to send the data to our Python backend.
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                body: formData
            });
            
            // The backend will send back a JSON response.
            const result = await response.json();

            if (!response.ok) {
                // If the server returns an error (e.g., status 500), handle it.
                // The 'detail' key is a standard from FastAPI for HTTP exceptions.
                throw new Error(result.detail || `API Error: ${response.status}`);
            }
            
            // If the request was successful, display the results.
            displayResults(result);
            
        } catch (error) {
            console.error('Error analyzing news:', error);
            alert(`An error occurred: ${error.message}`);
        } finally {
            // Always hide the loading spinner, even if there was an error.
            loadingOverlay.classList.add('hidden');
        }
    }

    /**
     * Updates the UI when a user selects an image file.
     * @param {Event} event - The file input change event.
     */
    function handleImageSelection(event) {
        const file = event.target.files[0];
        if (!file) return;

        fileNameDisplay.textContent = file.name; // Show the file name.
        
        // Use FileReader to show a preview of the image.
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreviewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    /**
     * Resets the image input field and hides the preview.
     */
    function removeSelectedImage() {
        imageInput.value = ''; // Clear the file input.
        fileNameDisplay.textContent = 'Choose an image';
        imagePreviewContainer.classList.add('hidden');
    }

    /**
     * Takes the result from the API and updates the HTML to show it.
     * @param {Object} result - The JSON data from the backend.
     */
    function displayResults(result) {
        // Switch views from the form to the results page.
        inputSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // --- Populate Prediction and Confidence ---
        const prediction = result.prediction || 'UNKNOWN';
        const confidence = result.confidence || 0;
        const confidencePercent = (confidence * 100).toFixed(0);
        
        predictionElement.textContent = prediction;
        predictionElement.className = `prediction ${prediction.toLowerCase()}`;
        
        confidenceMeter.className = `confidence-meter ${prediction.toLowerCase()}`;
        // Set the custom CSS property to animate the confidence bar.
        confidenceMeter.style.setProperty('--width', `${confidencePercent}%`);
        confidenceValue.textContent = `${confidencePercent}%`;
        
        // --- Populate Explanation ---
        explanationElement.textContent = result.explanation || 'No explanation provided.';
        
        // --- Populate Related News and Fact Checks ---
        displayRelatedNews(result.related_news);
        displayFactChecks(result.fact_checks);
        
        // Scroll down to the results smoothly.
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Renders the list of related news articles.
     * @param {Object} newsData - The related_news object from the API.
     */
    function displayRelatedNews(newsData) {
        relatedNewsContainer.innerHTML = ''; // Clear previous results.
        if (!newsData || newsData.status !== 'ok' || newsData.articles.length === 0) {
            relatedNewsContainer.innerHTML = '<p>No related news articles found.</p>';
            return;
        }
        
        newsData.articles.forEach(article => {
            // Using template literals to create HTML strings is cleaner than document.createElement for simple structures.
            const articleHTML = `
                <div class="news-item">
                    <div class="news-item-title">${article.title}</div>
                    <div class="news-item-source">Source: ${article.source}</div>
                    <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="news-item-link">Read Article <i class="fas fa-external-link-alt"></i></a>
                </div>`;
            relatedNewsContainer.innerHTML += articleHTML;
        });
    }

    /**
     * Renders the list of fact-checking results.
     * @param {Object} factChecks - An object with results from different sites.
     */
    function displayFactChecks(factChecks) {
        factChecksContainer.innerHTML = ''; // Clear previous results.
        let contentAdded = false;

        Object.entries(factChecks).forEach(([siteName, siteResult]) => {
            if (siteResult.found && siteResult.results && siteResult.results.length > 0) {
                contentAdded = true;
                const siteHTML = `<h4>${siteName.charAt(0).toUpperCase() + siteName.slice(1)}</h4>` +
                    siteResult.results.map(item => `
                        <div class="fact-check-item">
                            <div class="fact-check-item-title">${item.title}</div>
                            <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="fact-check-item-link">View Fact Check <i class="fas fa-external-link-alt"></i></a>
                        </div>
                    `).join('');
                factChecksContainer.innerHTML += siteHTML;
            }
        });

        if (!contentAdded) {
            factChecksContainer.innerHTML = '<p>No matches found on fact-checking sites.</p>';
        }
    }

    /**
     * Resets the entire UI to allow for a new analysis.
     */
    function resetForm() {
        newsForm.reset();
        removeSelectedImage();
        
        resultsSection.classList.add('hidden');
        inputSection.classList.remove('hidden');
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});