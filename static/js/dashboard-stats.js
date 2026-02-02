document.addEventListener("DOMContentLoaded", function() {
  let currentDays = 30;
  let ulrParams = null;

  function createChart(data, ctxElId, labelTextL, labelTextT) {
      let chart = null;
      const ctx = document.getElementById(ctxElId).getContext('2d');

      // Destroy existing chart if it exists
      if (chart) {
          chart.destroy();
      }

      const labels = data.map(d => {
          const date = new Date(d.date);
          return date.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric'
          });
      });

      const score = data.map(d => d.score);

      chart = new Chart(ctx, {
          type: 'line',
          data: {
              labels: labels,
              datasets: [{
                  label: labelTextL,
                  data: score,
                  borderColor: '#743afb',
                  backgroundColor: 'rgba(0, 123, 255, 0.1)',
                  borderWidth: 2,
                  fill: true,
                  tension: 0.4,
                  pointBackgroundColor: '#743afb',
                  pointBorderColor: '#ffffff',
                  pointBorderWidth: 2,
                  pointRadius: 4,
                  pointHoverRadius: 6
              }]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  title: {
                      display: true,
                      text: `${labelTextT} (${time_stat_label})`,
                      font: {
                          size: 16,
                          weight: 'bold'
                      }
                  },
                  legend: {
                      display: false
                  }
              },
              scales: {
                  y: {
                      beginAtZero: true,
                      ticks: {
                          stepSize: 1,
                          callback: function(value) {
                              return Math.floor(value) === value ? value : '';
                          }
                      },
                      title: {
                          display: true,
                          text: _LANGVARS.stats.numPlays
                      }
                  },
                  x: {
                      title: {
                          display: true,
                          text: 'Date'
                      }
                  }
              },
              interaction: {
                  intersect: false,
                  mode: 'index'
              },
              hover: {
                  animationDuration: 300
              },
              animation: {
                  duration: 1000,
                  easing: 'easeInOutQuart'
              }
          }
      });
  }

  createChart(daily_data_visit, 'viewsChart',
    _LANGVARS.stats.numPlays, _LANGVARS.stats.plays);
  createChart(daily_data_complete, 'completionsChart',
    _LANGVARS.stats.numCompletions, _LANGVARS.stats.completions);
  createChart(daily_data_time, 'timespentChart',
    _LANGVARS.stats.avgNumPlayed, _LANGVARS.stats.timePlayed);


  const tabButOvr = document.getElementById('dashboard-node-tabbut-ovr');
  const tabButUseract = document.getElementById('dashboard-node-tabbut-useract');
  const tabElOvr = document.getElementById('dashboard-node-stats-overview');
  const tabElUseract = document.getElementById('dashboard-node-stats-useract');

  tabButUseract.addEventListener('click', function() {
    tabElOvr.style.display = 'none';
    tabElUseract.style.display = 'block';
    tabButOvr.classList.remove('dashboard-node-stats-tab-selected');
    this.classList.add('dashboard-node-stats-tab-selected');
  });

  tabButOvr.addEventListener('click', function() {
    tabElOvr.style.display = 'flex';
    tabElUseract.style.display = 'none';
    tabButUseract.classList.remove('dashboard-node-stats-tab-selected');
    this.classList.add('dashboard-node-stats-tab-selected');
  });

  class DateRangePicker {
    constructor() {
        this.dateField = document.getElementById('dateField');
        this.dateDropdown = document.getElementById('dateDropdown');
        this.dropdownArrow = document.getElementById('dropdownArrow');
        this.dateFieldText = document.getElementById('dateFieldText');
        this.startDateInput = document.getElementById('startDate');
        this.endDateInput = document.getElementById('endDate');
        this.cancelBtn = document.getElementById('cancelBtn');
        this.applyBtn = document.getElementById('applyBtn');
        this.currentParamsEl = document.getElementById('currentParams');

        this.isOpen = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCurrentParams();
        this.setDefaultDates();
    }

    bindEvents() {
        // Toggle dropdown
        this.dateField.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.dateField.contains(e.target) && !this.dateDropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Button events
        this.cancelBtn.addEventListener('click', () => {
            this.closeDropdown();
            this.resetInputs();
        });

        this.applyBtn.addEventListener('click', () => {
            this.applyDateRange();
        });

        // Input validation
        this.startDateInput.addEventListener('change', () => this.validateDates());
        this.endDateInput.addEventListener('change', () => this.validateDates());

        // Prevent dropdown from closing when clicking inside
        this.dateDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    toggleDropdown() {
        if (this.isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        this.isOpen = true;
        this.dateField.classList.add('active');
        this.dateDropdown.classList.add('show');
        this.dropdownArrow.classList.add('rotated');
        this.validateDates();
    }

    closeDropdown() {
        this.isOpen = false;
        this.dateField.classList.remove('active');
        this.dateDropdown.classList.remove('show');
        this.dropdownArrow.classList.remove('rotated');
    }

    setDefaultDates() {
        const urlParams = new URLSearchParams(window.location.search);
        const startParam = urlParams.get('start_date');
        const endParam = urlParams.get('end_date');

        if (startParam && endParam) {
            this.startDateInput.value = startParam;
            this.endDateInput.value = endParam;
            this.updateFieldText(startParam, endParam);
        } else {
            // Set default to last 30 days
            const today = new Date();
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(today.getDate() - 30);

            this.startDateInput.value = this.formatDate(thirtyDaysAgo);
            this.endDateInput.value = this.formatDate(today);
        }

        if (startParam || endParam) {
          document.getElementById("dashboard-node-tabbut-ovr").scrollIntoView();
        }
    }

    validateDates() {
        const startDate = this.startDateInput.value;
        const endDate = this.endDateInput.value;

        const isValid = startDate && endDate && new Date(startDate) <= new Date(endDate);
        this.applyBtn.disabled = !isValid;

        return isValid;
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    updateFieldText(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);

        const formatOptions = { month: 'short', day: 'numeric', year: 'numeric' };
        const startFormatted = start.toLocaleDateString('en-US', formatOptions);
        const endFormatted = end.toLocaleDateString('en-US', formatOptions);

        this.dateFieldText.textContent = `${startFormatted} - ${endFormatted}`;
    }

    resetInputs() {
        this.setDefaultDates();
    }

    applyDateRange() {
        if (!this.validateDates()) return;

        const startDate = this.startDateInput.value;
        const endDate = this.endDateInput.value;

        // Update the field text
        this.updateFieldText(startDate, endDate);

        // Create new URL with parameters
        const url = new URL(window.location);
        url.searchParams.set('start_date', startDate);
        url.searchParams.set('end_date', endDate);

        // Redirect to new URL
        window.location.href = url.toString();
    }

    loadCurrentParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const startDate = urlParams.get('start_date');
        const endDate = urlParams.get('end_date');

        if (startDate && endDate) {
            this.currentParamsEl.textContent = `?start_date=${startDate}&end_date=${endDate}`;
        } else {
            this.currentParamsEl.textContent = 'None';
        }
     }
  }


  new DateRangePicker();


});
