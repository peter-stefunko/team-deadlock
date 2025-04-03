document.addEventListener("DOMContentLoaded", () => {
  let articles = [];
  let filteredArticles = [];
  let activeFilters = new Set(); // Start with all label filters active
  let selectedStartDate = "";
  let selectedEndDate = "";
  let selectedContentType = "all"; // Default content type
  let currentPage = 0;
  let loading = false;
  const articlesPerPage = 10;

  initializeFilters();

  // Ensure buttons exist before adding event listeners
  const searchButton = document.querySelector(".search-button");
  const generateButton = document.querySelector(".generate-button");
  const clearFiltersButton = document.querySelector(".clear-filters");
  const applyFiltersButton = document.querySelector(".apply-filters");

  if (searchButton) searchButton.addEventListener("click", fetchArticles);
  if (generateButton)
    generateButton.addEventListener("click", generateRandomInput);
  if (clearFiltersButton)
    clearFiltersButton.addEventListener("click", clearAllFilters);
  if (applyFiltersButton)
    applyFiltersButton.addEventListener("click", fetchArticles);

  document.querySelectorAll(".label-item").forEach((labelElement) => {
    const boxId = labelElement.querySelector(".label-box").id;
    labelElement.addEventListener("click", function () {
      toggleLabelFilter(boxId);
    });
  });

  document.querySelectorAll(".date-filter").forEach((input) => {
    input.addEventListener("change", trackDateFilters);
  });

  document.querySelectorAll(".selectable").forEach((contentType) => {
    contentType.addEventListener("click", function () {
      selectContentType(this);
    });
  });

  // ✅ Initialize Filters (Start with all labels selected)
  function initializeFilters() {
    document.querySelectorAll(".label-box").forEach((label) => {
      activeFilters.add(label.id);
    });
    updateLabelStyles();
  }

  // ✅ Track Date Selections
  function trackDateFilters() {
    selectedStartDate = document.querySelector(
      ".date-filter:nth-of-type(1)",
    ).value;
    selectedEndDate = document.querySelector(
      ".date-filter:nth-of-type(2)",
    ).value;
  }

  // ✅ Toggle Label Filters (Click to Deselect/Reselect)
  function toggleLabelFilter(label) {
    if (activeFilters.has(label)) {
      activeFilters.delete(label); // Deselect label
    } else {
      activeFilters.add(label); // Reselect label
    }
    updateLabelStyles();
  }

  // ✅ Update Label Styles
  function updateLabelStyles() {
    document.querySelectorAll(".label-box").forEach((box) => {
      if (activeFilters.has(box.id)) {
        box.classList.remove("selected-label-box");
      } else {
        box.classList.add("selected-label-box");
      }
    });
  }

  // ✅ Select Content Type (Only One at a Time)
  function selectContentType(selected) {
    document.querySelectorAll(".selectable").forEach((el) => {
      el.classList.remove("selected");
    });

    selected.classList.add("selected");

    if (selected.textContent.trim() === "News articles") {
      selectedContentType = "news_articles";
    } else if (selected.textContent.trim() === "Press releases") {
      selectedContentType = "press_releases";
    } else {
      selectedContentType = "all"; // Reset filter if "All" is selected
    }
  }

  // ✅ Clear All Filters
  function clearAllFilters() {
    activeFilters.clear();
    selectedStartDate = "";
    selectedEndDate = "";
    selectedContentType = "all"; // Reset content type

    document.querySelectorAll(".label-box").forEach((label) => {
      activeFilters.add(label.id);
    });

    document
      .querySelectorAll(".date-filter")
      .forEach((input) => (input.value = ""));
    document
      .querySelectorAll(".selectable")
      .forEach((el) => el.classList.remove("selected"));
    document.querySelector(".selectable").classList.add("selected"); // Select "All" by default

    updateLabelStyles();
  }

  function generateRandomInput() {
    blurAndDisable();
    let url = "http://193.187.129.146:8000/api/articles/generate_random_input";
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        document.querySelector(".search-input").value = data.query;
        unblurAndEnable();
      })
      .catch((error) => console.error("Error fetching articles:", error));
  }

  // ✅ Fetch Articles
  function fetchArticles() {
    const query = document.querySelector(".search-input").value;
    document.getElementsByClassName('search-input')[0].readOnly = true;


    startLoading();
    let url = `http://193.187.129.146:8000/api/articles/search?query=${encodeURIComponent(query)}`;

    let selectedCategories = [];
    document.querySelectorAll(".category.selected").forEach((category) => {
      selectedCategories.push(category.innerText);
    });

    if (selectedCategories.length > 0)
      url += `&cat=${selectedCategories.join(",")}`;

    if (selectedContentType != "all") {
      url += `&tp=${encodeURIComponent(selectedContentType)}`;
    }
    if (selectedStartDate) {
      url += `&start_dt=${encodeURIComponent(selectedStartDate)}`;
    }
    if (selectedEndDate) {
      url += `&end_dt=${encodeURIComponent(selectedEndDate)}`;
    }
    if (activeFilters.size > 0 && activeFilters.size != 11) {
      url += `&cls=${Array.from(activeFilters).join(",")}`;
    }

    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          articles = data;
          filteredArticles = articles;
          updateArticleCount(filteredArticles.length);
          currentPage = 0;
          renderArticles();
          document.getElementsByClassName('search-input')[0].readOnly = false;
         } else {
          console.error("Expected an array but got:", data);
        }
      })
      .catch((error) => console.error("Error fetching articles:", error));
  }

  // ✅ Update Article Count
  function updateArticleCount(count) {
    const articleCountEl = document.getElementById("numOfArticles");
    if (articleCountEl) {
      articleCountEl.textContent = `${count}`;
    }
  }

  function upvote(articleId) {
    let url = `http://193.187.129.146:8000/api/articles/trusted?article_id=${articleId}`;
    fetch(url)
      .then(response => response.json())
      .then(data => {
        alert("Article has been marked as trusted.");
      })
      .catch(error => {
        console.error("Error fetching article data:", error);
      });
    }
  function downvote(articleId) {
      let url = `http://193.187.129.146:8000/api/articles/not_trusted?article_id=${articleId}`;
  
      fetch(url)
          .then(response => response.json())
          .then(data => {
            alert("Article has been marked as untrusted.");
          })
          .catch(error => {
              console.error("Error fetching article data:", error);
          });
  }

  // ✅ Render Articles
// ✅ Render Articles
function renderArticles() {
  const articleContainer = document.getElementById("article-container");
  if (!articleContainer) return;

  articleContainer.innerHTML = "";

  const start = currentPage * articlesPerPage;
  const end = Math.min(start + articlesPerPage, filteredArticles.length);
  const pageArticles = filteredArticles.slice(start, end);

  if (pageArticles.length === 0) {
      articleContainer.innerHTML = `<p style="color: gray;">No articles found.</p>`;
      updateArticleCount(0);
      return;
  }

  updateArticleCount(filteredArticles.length);

  pageArticles.forEach((article, index) => {
      const articleElement = document.createElement("div");
      articleElement.style.padding = "20px";
      articleElement.style.borderBottom = "1px solid #ccc";

      const formattedDate = formatDate(article.publishedAt || article.scannedAt);

      const trustFactor = Math.round(((article.trustFactor || 0) * 100) / 20 * 10) / 10;

      let starImage, trustFactorColor;
      if (trustFactor >= 3.9) {
          starImage = "filled-star.svg";
          trustFactorColor = "#005c01"; 
      } else if (trustFactor >= 2.5 && trustFactor <= 3.8) {
          starImage = "half-filled-star.svg";
          trustFactorColor = '#c0b826'; 
      } else {
          starImage = "empty-star.svg";
          trustFactorColor = "#8b0a0c"; 
      }

      articleElement.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: start; width: 100%; flex-wrap: wrap;">
        <a href="${article.url}" target="_blank" 
          style="font-size:18px; text-decoration:underline; color:white;
                max-width: 87%; word-wrap: break-word;">
          ${article.title}
        </a>
        <span style="color: #b4b4b4; font-size: 14px; white-space: nowrap; margin-left: auto;">
          ${formattedDate}
        </span>
      </div>
    
      <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-top: 5px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          
          <!-- Trust Factor -->
          <span style="color: ${trustFactorColor}; font-size: 14px;">
            ${trustFactor}
          </span>
          <img src="${starImage}" 
              alt="Trust Factor Star" 
              width="17px" height="17px" 
              style="filter: ${trustFactorColor === '#8b0a0c' ? 'invert(13%) sepia(88%) saturate(2812%) hue-rotate(349deg) brightness(90%) contrast(101%);' :
                              trustFactorColor === '#c0b826' ? 'invert(79%) sepia(90%) saturate(401%) hue-rotate(1deg) brightness(78%) contrast(95%);' :
                              trustFactorColor === '#005c01' ? 'invert(24%) sepia(98%) saturate(499%) hue-rotate(82deg) brightness(90%) contrast(101%);' :
                              'invert(100%) brightness(100%)'};">
          
          <!-- Publisher -->
          <span style="color: #a5a5a5; font-size: 14px;">
            ${article.publisher}
          </span>
        </div>
    
        <!-- Like & Dislike Buttons Aligned Right -->
        <div style="display: flex; gap: 5px; margin-left: auto;">
          <button id="like-btn-${index}" 
                  onclick="toggleLike(${index})" 
                  style="border: none; background: none; font-size: 16px; cursor: pointer; color: gray;">
            <img alt="Upvote SVG Vector Icon" fetchpriority="high" decoding="async" data-nimg="1" 
                 style="width:18px;height:18px;filter: invert(24%) sepia(98%) saturate(499%) hue-rotate(82deg) brightness(90%) contrast(101%);" 
                 src="upvote.svg">
          </button>
          <button id="dislike-btn-${index}" 
                  onclick="toggleDislike(${index})" 
                  style="border: none; background: none; font-size: 16px; cursor: pointer; color: gray;">
            <img alt="Downvote SVG Vector Icon" fetchpriority="high" decoding="async" data-nimg="1" 
                 style="width:18px;height:18px;filter: invert(13%) sepia(88%) saturate(2812%) hue-rotate(349deg) brightness(90%) contrast(101%);" 
                 src="downvote.svg">
          </button>
        </div>
      </div>
    `;

        articleContainer.appendChild(articleElement);
    });

    renderPaginationControls();
}


  // ✅ Format Date
  function formatDate(isoString) {
    if (!isoString) return "Unknown Date"; // Prevents errors for missing dates
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  // ✅ Render Pagination
  function renderPaginationControls() {
    const controls = document.getElementById("pagination-controls");
    if (!controls) return;
    controls.innerHTML = "";

    if (currentPage > 0) {
      const prevButton = document.createElement("button");
      prevButton.textContent = "Previous";
      prevButton.classList.add("pagination-button", "prev");
      prevButton.onclick = () => {
        currentPage--;
        renderArticles();
      };
      controls.appendChild(prevButton);
    }

    if ((currentPage + 1) * articlesPerPage < filteredArticles.length) {
      const nextButton = document.createElement("button");
      nextButton.textContent = "Next";
      nextButton.classList.add("pagination-button", "next");
      nextButton.onclick = () => {
        currentPage++;
        renderArticles();
      };
      controls.appendChild(nextButton);
    }
  }
});

function showTooltip() {
  const tooltip = document.getElementById("tooltip");
  tooltip.style.visibility = "visible";
  tooltip.style.opacity = "1";
}

function moveTooltip(event) {
  const tooltip = document.getElementById("tooltip");
  tooltip.style.left = event.pageX + 15 + "px"; // Slightly offset from cursor
  tooltip.style.top = event.pageY + 15 + "px";
}

function hideTooltip() {
  const tooltip = document.getElementById("tooltip");
  tooltip.style.visibility = "hidden";
  tooltip.style.opacity = "0";
}

document.addEventListener("DOMContentLoaded", function () {
  const labelItems = document.querySelectorAll(".label-item");
  const numOfLabelsSelected = document.getElementById("numOfLabelsSelected");

  let selectedLabelsCount = labelItems.length; // Start with all labels selected

  function updateLabelCount() {
    numOfLabelsSelected.textContent = `(${selectedLabelsCount})`;
  }

  labelItems.forEach((item) => {
    const labelBox = item.querySelector(".label-box");

    // Mark all labels as initially selected
    item.classList.add("selected");
    labelBox.classList.remove("selected-label-box");

    item.addEventListener("click", function () {
      if (item.classList.contains("selected")) {
        item.classList.remove("selected");
        labelBox.classList.add("selected-label-box");
        selectedLabelsCount = Math.max(0, selectedLabelsCount - 1); // Ensure count never goes negative
      } else {
        item.classList.add("selected");
        labelBox.classList.remove("selected-label-box");
        selectedLabelsCount++;
      }

      updateLabelCount();
    });
  });

  // Set initial count
  updateLabelCount();
});

document.addEventListener("DOMContentLoaded", () => {
  const categoryButtons = document.querySelectorAll(".categories button");
  const selectedCategories = new Set();

  // Create and insert the counter element
  const counterElement = document.createElement("span");
  counterElement.id = "categoryCount";
  counterElement.style.marginLeft = "10px";
  counterElement.style.color = "white";
  counterElement.style.fontWeight = "bold";
  document.querySelector(".categories").appendChild(counterElement);

  // Function to update count and style
  function updateCategorySelection(button) {
    const categoryName = button.textContent.trim();

    if (selectedCategories.has(categoryName)) {
      selectedCategories.delete(categoryName);
      button.style.backgroundColor = "#2b2d31"; // Reset to default
      button.style.color = "white";
    } else {
      selectedCategories.add(categoryName);
      button.style.backgroundColor = "#515155"; // Blue color
      button.style.color = "white";
    }
  }

  // Add event listeners to each category button
  categoryButtons.forEach((button) => {
    button.addEventListener("click", function () {
      updateCategorySelection(this);
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  let activeFilters = new Set(); // Store active filters
  const totalLabels = 11; // Total number of labels
  const numOfLabelsSelected = document.getElementById("numOfLabelsSelected");

  // Ensure all labels are initially selected
  initializeFilters();

  document
    .querySelector(".unselect-all")
    .addEventListener("click", unselectAllLabels);

  document.querySelectorAll(".label-item").forEach((labelElement) => {
    const boxId = labelElement.querySelector(".label-box").id;
    labelElement.addEventListener("click", function () {
      toggleLabelFilter(boxId);
    });
  });

  function initializeFilters() {
    document.querySelectorAll(".label-box").forEach((label) => {
      activeFilters.add(label.id);
    });
    updateLabelStyles();
    updateLabelCount();
  }

  function toggleLabelFilter(label) {
    if (activeFilters.has(label)) {
      activeFilters.delete(label);
    } else {
      activeFilters.add(label);
    }
    updateLabelStyles();
    updateLabelCount();
  }

  function unselectAllLabels() {
    activeFilters.clear(); // Remove all active filters

    document.querySelectorAll(".label-box").forEach((label) => {
      label.classList.add("selected-label-box"); // Hide background color
    });

    updateLabelCount();
  }

  function updateLabelStyles() {
    document.querySelectorAll(".label-box").forEach((box) => {
      if (activeFilters.has(box.id)) {
        box.classList.remove("selected-label-box"); // Show background color
      } else {
        box.classList.add("selected-label-box"); // Hide background color
      }
    });
  }

  function updateLabelCount() {
    numOfLabelsSelected.textContent = `(${activeFilters.size})`;
  }
});

document.addEventListener("DOMContentLoaded", function () {
  let inputField = document.querySelector(".search-input");
});

function startLoading() {
  articleElement = document.getElementById("article-container");
  articleElement.innerHTML = "<div style='width: 100%; height: 50%; display: flex; align-items: center; justify-content: center;'><div class='loader'></div></div>";
};

function blurAndDisable() {
  document.querySelector('.search-input').classList.add('blur-placeholder');
  document.querySelector('.search-input').classList.add('blur');
  document.getElementsByClassName('search-input')[0].readOnly = true;
}

function unblurAndEnable() {
  document.querySelector('.search-input').classList.remove('blur-placeholder');
  document.querySelector('.search-input').classList.remove('blur');
  document.getElementsByClassName('search-input')[0].readOnly = false;
};
