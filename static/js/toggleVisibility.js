// toggleVisibility.js

function toggleSectionVisibilityClass(sectionClass) {
    var sections = document.getElementsByClassName(sectionClass);
    for (var i = 0; i < sections.length; i++) {
        sections[i].classList.toggle('hidden');
    }
}

// function toggleSectionVisibility(sectionId) {
//     var sectionTitle = document.getElementById(sectionId);
//     var sectionContent = document.getElementById(sectionId + "-content");

//     if (sectionTitle && sectionContent) {
//         sectionTitle.classList.toggle('hidden');
//         sectionContent.classList.toggle('hidden');
//     }
// }

// function toggleSectionVisibility(sectionId) {
//     var sectionContent = document.getElementById(sectionId + "-content");
//     if (sectionContent) {
//         sectionContent.classList.toggle('hidden');
//     }
// }

function toggleSectionVisibility(sectionId) {
    const content = document.getElementById(sectionId + '-content');
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
    } else {
        content.classList.add('hidden');
    }
}


function toggleCollapsible_old(buttonId, contentId) {
    const content = document.getElementById(contentId);
    const button = document.getElementById(buttonId);

    if (content.style.maxHeight) {
        // If the content is expanded, collapse it
        content.style.maxHeight = null;
        button.classList.remove('active');
    } else {
        // If the content is collapsed, expand it
        content.style.maxHeight = content.scrollHeight + "px";
        button.classList.add('active');
    }
}

function toggleCollapsible(buttonId, contentId, isNavSection = false) {
    const content = document.getElementById(contentId);
    const button = document.getElementById(buttonId);

    if (isNavSection) {
        // For the navigation section, collapse all other navigation sections
        const allContents = document.querySelectorAll('.nav-collapsible-content');
        const allButtons = document.querySelectorAll('.nav-collapsible');

        allContents.forEach((otherContent) => {
            if (otherContent !== content) {
                otherContent.style.maxHeight = null;
            }
        });

        allButtons.forEach((otherButton) => {
            if (otherButton !== button) {
                otherButton.classList.remove('active');
            }
        });
    }

    // Toggle the selected section
    if (content.style.maxHeight) {
        // Collapse the selected section
        content.style.maxHeight = null;
        button.classList.remove('active');
    } else {
        // Expand the selected section
        content.style.maxHeight = content.scrollHeight + "px";
        button.classList.add('active');
    }
}

document.getElementById('loadJsonButton').addEventListener('click', function() {
    const jsonFileInput = document.getElementById('jsonFile');
    const file = jsonFileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const jsonData = JSON.parse(e.target.result);

                // Function to safely assign value if the element exists
                function assignValue(fieldId, value) {
                    const field = document.getElementById(fieldId);
                    if (field) {
                        field.value = value || ''; // Set to empty string if value is null/undefined
                    }
                }

                // Populate form fields with JSON data
                assignValue('scenarioName', jsonData.scenarioName);
                assignValue('scenarioYears', jsonData.scenarioYears);
                assignValue('spouse1YearlyIncomeBase', jsonData.spouse1YearlyIncomeBase);
                assignValue('spouse1YearlyIncomeBonus', jsonData.spouse1YearlyIncomeBonus);
                assignValue('spouse2YearlyIncomeBase', jsonData.spouse2YearlyIncomeBase);
                assignValue('spouse2YearlyIncomeBonus', jsonData.spouse2YearlyIncomeBonus);
                assignValue('annualIncome', jsonData.annualIncome);

                // Add similar lines for other fields
                // assignValue('fieldId', jsonData.someValue);
            } catch (error) {
                console.error("Error parsing JSON data:", error);
                alert("Error parsing JSON data. Please check the file format.");
            }
        };
        reader.readAsText(file);
    }
});


// Function to populate the form with JSON data
function populateForm(data) {
    // Basic fields
    document.getElementById('scenarioName').value = data.scenarioName || '';
    document.getElementById('scenarioYears').value = data.years || 'Not Found';
    
    // Spouse 1 income
    document.getElementById('spouse1YearlyIncomeBase').value = data.spouse1_yearly_income_base || '';
    document.getElementById('spouse1YearlyIncomeBonus').value = data.spouse1_yearly_income_bonus || '';
    document.getElementById('spouse1YearlyIncomeQuarterly').value = data.spouse1_yearly_income_quarterly || '';
    document.getElementById('stockgrant').value = data.stockgrant || '';
    
    // Spouse 1 pre-tax investments
    document.getElementById('spouse1RetirementContributionPretax').value = data.SPOUSE1_PRETAX_INVESTMENTS?.spouse1_retirement_contribution_pretax || '';
    document.getElementById('spouse1HSAPretax').value = data.SPOUSE1_PRETAX_INVESTMENTS?.spouse1_hsa_pretax || '';
    document.getElementById('spouse1SerplusPretax').value = data.SPOUSE1_PRETAX_INVESTMENTS?.spouse1_serplus_pretax || '';
    
    // Spouse 1 post-tax investments
    document.getElementById('spouse1RetirementContributionPosttax').value = data.SPOUSE1_POSTTAX_INVESTMENTS?.spouse1_retirement_contribution_posttax || '';
    document.getElementById('stocksEsppPosttax').value = data.SPOUSE1_POSTTAX_INVESTMENTS?.stocks_espp_posttax || '';

    // Spouse 2 income and investments
    document.getElementById('spouse2YearlyIncomeBase').value = data.spouse2_yearly_income_base || '';
    document.getElementById('spouse2YearlyIncomeBonus').value = data.spouse2_yearly_income_bonus || '';
    document.getElementById('spouse2YearlyIncomeQuarterly').value = data.spouse2_yearly_income_quarterly || '';
    
    document.getElementById('spouse2RetirementContributionPretax').value = data.SPOUSE2_PRETAX_INVESTMENTS?.spouse2_retirement_contribution_pretax || '';
    document.getElementById('spouse2HSAPretax').value = data.SPOUSE2_PRETAX_INVESTMENTS?.spouse2_hsa_pretax || '';
    document.getElementById('spouse2SerplusPretax').value = data.SPOUSE2_PRETAX_INVESTMENTS?.spouse2_serplus_pretax || '';
    
    document.getElementById('spouse2RetirementContributionPosttax').value = data.SPOUSE2_POSTTAX_INVESTMENTS?.spouse2_retirement_contribution_posttax || '';
    document.getElementById('stocksEsppPosttax').value = data.SPOUSE2_POSTTAX_INVESTMENTS?.stocks_espp_posttax || '';

    // Taxes
    document.getElementById('yearlyPropertyTax').value = data.yearly_property_tax || '';
    document.getElementById('assumedTaxRate').value = data.assumed_tax_rate || '';
    document.getElementById('federalTaxRateSingle').value = data.federal_tax_rate_single || '';
    document.getElementById('stateTaxRateSingle').value = data.state_tax_rate_single || '';
    document.getElementById('federalTaxRateDual').value = data.federal_tax_rate_dual || '';
    document.getElementById('stateTaxRateDual').value = data.state_tax_rate_dual || '';

    // Expenses
    document.getElementById('groceries').value = data.Groceries || '';
    document.getElementById('monthlyClothing').value = data.monthly_clothing || '';
    document.getElementById('monthlyHouseMaintenance').value = data.monthly_house_maintenance || '';
    document.getElementById('totalCamp').value = data.total_camp || '';
    document.getElementById('carPurchase').value = data.car_purchase || '';
    document.getElementById('fitnessExpenses').value = data.fitness || '';
    document.getElementById('miscellaneous').value = data.miscellaneous || '';

    // Car monthly expenses
    document.getElementById('carMaintenance').value = data.CAR_MONTHLY?.car_maintenance || '';
    document.getElementById('carRepair').value = data.CAR_MONTHLY?.car_repair || '';
    document.getElementById('carGasExpense').value = data.CAR_MONTHLY?.car_gas_expense || '';
    
    // Athletic team
    document.getElementById('athleticTeamSummerFee').value = data.ATHLETIC_TEAM?.team_summerfee_kid1 || '';
    document.getElementById('athleticTeamFallFee').value = data.ATHLETIC_TEAM?.team_fallfee_kid1 || '';
    document.getElementById('athleticTeamEquipment').value = data.ATHLETIC_TEAM?.equipment || '';
    document.getElementById('athleticTeamClothing').value = data.ATHLETIC_TEAM?.clothing || '';
    document.getElementById('athleticTeamGas').value = data.ATHLETIC_TEAM?.gas || '';
    document.getElementById('athleticTeamFlight').value = data.ATHLETIC_TEAM?.flight || '';
    document.getElementById('athleticTeamGameEntry').value = data.ATHLETIC_TEAM?.game_entry || '';
    document.getElementById('athleticTeamTravelHousing').value = data.ATHLETIC_TEAM?.travel_housing || '';

    // Utilities
    document.getElementById('waterUtility').value = data.UTILITIES?.water_utility || '';
    document.getElementById('gasElectric').value = data.UTILITIES?.gas_electric || '';
    document.getElementById('internet').value = data.UTILITIES?.internet || '';
    document.getElementById('garbage').value = data.UTILITIES?.garbage || '';
    document.getElementById('mobilePhone').value = data.UTILITIES?.mobile_phone || '';

    // Insurance
    document.getElementById('carInsurance').value = data.INSURANCE?.car_insurance || '';
    document.getElementById('homeInsurance').value = data.INSURANCE?.home_insurance || '';
    document.getElementById('umbrellaInsurance').value = data.INSURANCE?.umbrella_insurance || '';
    document.getElementById('dentalInsurance').value = data.INSURANCE?.dental_insurance || '';
    document.getElementById('visionInsurance').value = data.INSURANCE?.vision_insurance || '';
    document.getElementById('hfsa').value = data.INSURANCE?.hfsa || '';

    // Subscriptions
    document.getElementById('streamingTV').value = data.SUBSCRIPTIONS?.streaming_tv || '';
    document.getElementById('books').value = data.SUBSCRIPTIONS?.books || '';
    document.getElementById('streamMusic').value = data.SUBSCRIPTIONS?.stream_music || '';
    document.getElementById('professionalSubscriptions').value = data.SUBSCRIPTIONS?.professional_subscriptions || '';
    document.getElementById('videoSubscriptions').value = data.SUBSCRIPTIONS?.video || '';
    document.getElementById('photoSubscriptions').value = data.SUBSCRIPTIONS?.photo || '';
    document.getElementById('shoppingSubscriptions').value = data.SUBSCRIPTIONS?.shopping || '';

    // House details
    document.getElementById('currentHouseValue').value = data.house?.value || '';
    document.getElementById('sellHouse').checked = data.house?.sell_house || false;

    // Retirement, investment, children, etc. can be populated similarly
}
