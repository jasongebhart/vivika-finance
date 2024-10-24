// toggleVisibility.js

function toggleSectionVisibilityClass(sectionClass) {
    var sections = document.getElementsByClassName(sectionClass);
    for (var i = 0; i < sections.length; i++) {
        sections[i].classList.toggle('hidden');
    }
}

function toggleSectionVisibility(sectionId) {
    const content = document.getElementById(sectionId + '-content');
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
    } else {
        content.classList.add('hidden');
    }
}

function toggleCollapsible(buttonId, contentId, isNavSection = false, group = null) {
    const content = document.getElementById(contentId);
    const button = document.getElementById(buttonId);

    if (isNavSection) {
        // For the navigation section, collapse all other navigation sections
        const allContents = document.querySelectorAll('.nav-collapsible-content');
        const allButtons = document.querySelectorAll('.nav-collapsible');

        allContents.forEach((otherContent) => {
            if (otherContent !== content) {
                otherContent.style.maxHeight = null; // Collapse other sections
                localStorage.setItem(otherContent.id, 'collapsed'); // Save state
            }
        });

        allButtons.forEach((otherButton) => {
            if (otherButton !== button) {
                otherButton.classList.remove('active');
            }
        });

        // Store which group (viable, not-viable, or all) was last opened
        if (group) {
            localStorage.setItem('lastGroupOpened', group);
        }
    }

    // Toggle the selected section
    if (content.style.maxHeight) {
        // Collapse the selected section
        content.style.maxHeight = null;
        button.classList.remove('active');
        localStorage.setItem(contentId, 'collapsed'); // Save state
    } else {
        // Expand the selected section
        content.style.maxHeight = content.scrollHeight + "px";
        button.classList.add('active');
        localStorage.setItem(contentId, 'expanded'); // Save state
    }
}


function restoreGroupState() {
    const lastGroupOpened = localStorage.getItem('lastGroupOpened');
    if (lastGroupOpened) {
        // Automatically expand the last opened group (viable/not-viable)
        const groupButton = document.querySelector(`[data-group="${lastGroupOpened}"]`);
        if (groupButton) {
            groupButton.click();
        }
    }
}


// Function to restore the last active section from localStorage
function restoreCollapsibleState() {
    // Restore the state for viable-content, not-viable-content, and all-content
    const viableContentState = localStorage.getItem('viable-content');
    const notViableContentState = localStorage.getItem('not-viable-content');
    const allContentState = localStorage.getItem('all-content');

    const viableButton = document.querySelector(`[data-target="viable-content"]`);
    const viableContent = document.getElementById('viable-content');
    const notViableButton = document.querySelector(`[data-target="not-viable-content"]`);
    const notViableContent = document.getElementById('not-viable-content');
    const allButton = document.querySelector(`[data-target="all-content"]`);
    const allContent = document.getElementById('all-content');

    // Restore viable-content state
    if (viableContentState === 'expanded') {
        viableContent.style.maxHeight = viableContent.scrollHeight + "px";
        viableButton.classList.add('active');
    } else {
        viableContent.style.maxHeight = null;
        viableButton.classList.remove('active');
    }

    // Restore not-viable-content state
    if (notViableContentState === 'expanded') {
        notViableContent.style.maxHeight = notViableContent.scrollHeight + "px";
        notViableButton.classList.add('active');
    } else {
        notViableContent.style.maxHeight = null;
        notViableButton.classList.remove('active');
    }

    // Restore all-content state
    if (allContentState === 'expanded') {
        allContent.style.maxHeight = allContent.scrollHeight + "px";
        allButton.classList.add('active');
    } else {
        allContent.style.maxHeight = null;
        allButton.classList.remove('active');
    }
}

function toggleCollapsible_old(buttonId, contentId, isNavSection = false) {
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

document.addEventListener("DOMContentLoaded", () => {
    // Add event listener to the load JSON button
    document.getElementById('loadJsonButton').addEventListener('click', loadJsonFile);
    // Event listener for adding a new investment
    document.getElementById('addInvestmentBtn').addEventListener('click', addInvestment);
    // Restore the last opened viable/not-viable section
    restoreGroupState();
    // Restore the saved state of collapsible sections
    restoreCollapsibleState();
});

// Function to load and read the selected JSON file
async function loadJsonFile() {
    const fileInput = document.getElementById('jsonFile');
    if (fileInput.files.length === 0) {
        alert("Please select a JSON file.");
        return;
    }

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = async (event) => {
        try {
            const uniqueScenarioData = JSON.parse(event.target.result);

            // Load general finance data
            const generalFinanceData = await loadGeneralFinance();

            // Merge general finance data with unique scenario data
            const combinedData = { ...generalFinanceData, ...uniqueScenarioData };

            // Populate the form with the combined data
            populateForm(combinedData);
        } catch (error) {
            console.error('Error parsing JSON:', error);
            alert("There was an error parsing the JSON file.");
        }
    };

    reader.onerror = (error) => {
        console.error('Error reading file:', error);
        alert("There was an error reading the file.");
    };

    reader.readAsText(file); // Read the file as text
}

// Function to populate the form fields with data
function populateForm(data) {
    // Helper function to set the value of an input field
    const setValue = (id, value = '') => {
        const element = document.getElementById(id);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = !!value; // For checkboxes, use checked property
            } else {
                element.value = value; // For other input types, set value
            }
        }
    };

    // Destructure data for easier access
    const {
        years = 'Not Found',
        assumption_description = '',
        annual_rent = '',
        annual_vacation = '',
        additional_insurance = '',
        interest_rate = '',
        yearly_expense = '',
        yearly_gain = '',
        RETIREMENT = [],
        gains = [0, 0, 0, 0, 0, 0, 0, 0],
        spouse1_yearly_income_base = '',
        spouse1_yearly_income_bonus = '',
        spouse1_yearly_income_quarterly = '',
        stockgrant = '',
        SPOUSE1_PRETAX_INVESTMENTS = {},
        SPOUSE1_POSTTAX_INVESTMENTS = {},
        spouse2_yearly_income_base = '',
        spouse2_yearly_income_bonus = '',
        spouse2_yearly_income_quarterly = '',
        SPOUSE2_PRETAX_INVESTMENTS = {},
        SPOUSE2_POSTTAX_INVESTMENTS = {},
        employee_stock_purchase = '',
        yearly_property_tax = '',
        assumed_tax_rate = '',
        federal_tax_rate_single = '',
        state_tax_rate_single = '',
        federal_tax_rate_dual = '',
        state_tax_rate_dual = '',
        Groceries = '',
        monthly_clothing = '',
        monthly_house_maintenance = '',
        miscellaneous = '',
        CAR_MONTHLY = {},
        ATHLETIC_TEAM = {},
        UTILITIES = {},
        INSURANCE = {},
        SUBSCRIPTIONS = {},
        investment_balance = '',
        retirement_principal = '',
        initial_contribution = '',
        increase_contribution = '',
        house = {},
        new_house = {},
        home_tenure = '',
        residence_location = '',
        current_residence_location = '',
        capital_gain_exclusion = '',
        parent_one = '',
        parent_two = '',
        investment = {},
        KIDS_ACTIVITIES = {},
        highschool = '',
        children = {}
    } = data;

    // Basic fields
    setValue('assumptionDescription', assumption_description);
    setValue('scenarioYears', years);
    setValue('highschool', highschool);
    setValue('annualRent', annual_rent);
    setValue('annualVacation', annual_vacation);
    setValue('interestRate', interest_rate);

    // Situation
    setValue('homeTenure', home_tenure);
    setValue('residenceLocation', residence_location);
    setValue('currentResidenceLocation', current_residence_location);
    setValue('capitalGainExclusion', capital_gain_exclusion);
    setValue('parentOne', parent_one);
    setValue('parentTwo', parent_two);

    // Spouse 1 income
    setValue('spouse1YearlyIncomeBase', spouse1_yearly_income_base);
    setValue('spouse1YearlyIncomeBonus', spouse1_yearly_income_bonus);
    setValue('spouse1YearlyIncomeQuarterly', spouse1_yearly_income_quarterly);
    setValue('stockgrant', stockgrant);

    // Spouse 1 pre-tax investments
    setValue('spouse1RetirementContributionPretax', SPOUSE1_PRETAX_INVESTMENTS.spouse1_retirement_contribution_pretax);
    setValue('spouse1HSAPretax', SPOUSE1_PRETAX_INVESTMENTS.spouse1_hsa_pretax);
    setValue('spouse1SerplusPretax', SPOUSE1_PRETAX_INVESTMENTS.spouse1_serplus_pretax);

    // Spouse 1 post-tax investments
    setValue('spouse1RetirementContributionPosttax', SPOUSE1_POSTTAX_INVESTMENTS.spouse1_retirement_contribution_posttax);
    setValue('stocksEsppPosttax', SPOUSE1_POSTTAX_INVESTMENTS.stocks_espp_posttax);

    // Spouse 2 income and investments
    setValue('spouse2YearlyIncomeBase', spouse2_yearly_income_base);
    setValue('spouse2YearlyIncomeBonus', spouse2_yearly_income_bonus);
    setValue('spouse2YearlyIncomeQuarterly', spouse2_yearly_income_quarterly);
    
    setValue('spouse2RetirementContributionPretax', SPOUSE2_PRETAX_INVESTMENTS.spouse2_retirement_contribution_pretax);
    setValue('spouse2HSAPretax', SPOUSE2_PRETAX_INVESTMENTS.spouse2_hsa_pretax);
    setValue('spouse2SerplusPretax', SPOUSE2_PRETAX_INVESTMENTS.spouse2_serplus_pretax);
    
    setValue('spouse2RetirementContributionPosttax', SPOUSE2_POSTTAX_INVESTMENTS.spouse2_retirement_contribution_posttax);
    setValue('stocksEsppPosttax', SPOUSE2_POSTTAX_INVESTMENTS.stocks_espp_posttax);

    // Gain
    setValue('annualSurplus', yearly_gain);

    // Taxes
    setValue('yearlyPropertyTax', yearly_property_tax);
    setValue('assumedTaxRate', assumed_tax_rate);
    setValue('federalTaxRateSingle', federal_tax_rate_single);
    setValue('stateTaxRateSingle', state_tax_rate_single);
    setValue('federalTaxRateDual', federal_tax_rate_dual);
    setValue('stateTaxRateDual', state_tax_rate_dual);

    // Expenses
    setValue('annualExpenses', yearly_expense);
    setValue('groceries', Groceries);
    setValue('monthlyClothing', monthly_clothing);
    setValue('monthlyHouseMaintenance', monthly_house_maintenance);
    setValue('miscellaneous', miscellaneous);

    // Car monthly expenses
    setValue('carMaintenance', CAR_MONTHLY.car_maintenance);
    setValue('carRepair', CAR_MONTHLY.car_repair);
    setValue('carFuelExpense', CAR_MONTHLY.car_gas_expense);
    setValue('carPurchase', CAR_MONTHLY.car_purchase);
    
    // Athletic team expenses
    setValue('athleticTeamSummerFee', ATHLETIC_TEAM.team_summerfee_kid1);
    setValue('athleticTeamFallFee', ATHLETIC_TEAM.team_fallfee_kid1);
    setValue('athleticTeamEquipment', ATHLETIC_TEAM.equipment);
    setValue('athleticTeamClothing', ATHLETIC_TEAM.clothing);
    setValue('athleticTeamGas', ATHLETIC_TEAM.gas);
    setValue('athleticTeamFlight', ATHLETIC_TEAM.flight);
    setValue('athleticTeamGameEntry', ATHLETIC_TEAM.game_entry);
    setValue('athleticTeamTravelHousing', ATHLETIC_TEAM.travel_housing);

    // Utilities
    setValue('water', UTILITIES.water);
    setValue('electric', UTILITIES.electric);
    setValue('gas', UTILITIES.gas);
    setValue('internet', UTILITIES.internet);
    setValue('garbage', UTILITIES.garbage);
    setValue('mobilePhone', UTILITIES.mobile_phone);

    // Insurance
    setValue('carInsurance', INSURANCE.car_insurance);
    setValue('homeInsurance', INSURANCE.home_insurance);
    setValue('umbrellaInsurance', INSURANCE.umbrella_insurance);
    setValue('dentalInsurance', INSURANCE.dental_insurance);
    setValue('visionInsurance', INSURANCE.vision_insurance);
    setValue('hfsa', INSURANCE.hfsa);
    setValue('additionalInsurance', additional_insurance);

    // Subscriptions
    setValue('streamingTV', SUBSCRIPTIONS.streaming_tv);
    setValue('books', SUBSCRIPTIONS.books);
    setValue('streamMusic', SUBSCRIPTIONS.stream_music);
    setValue('professionalSubscriptions', SUBSCRIPTIONS.professional_subscriptions);
    setValue('videoSubscriptions', SUBSCRIPTIONS.video);
    setValue('photoSubscriptions', SUBSCRIPTIONS.photo);
    setValue('shoppingSubscriptions', SUBSCRIPTIONS.shopping);

    // House details
    setValue('currentHouseValue', house.value);
    setValue('cost_basis', house.cost_basis); // Add this line for cost_basis
    setValue('closing_costs', house.closing_costs); // Add this line for closing costs
    setValue('home_improvement', house.home_improvement); // Add this line for home improvement
    setValue('mortgage_principal', house.mortgage_principal); // Add this line for mortgage principal
    setValue('commission_rate', house.commission_rate); // Add this line for commission rate
    setValue('annual_growth_rate', house.annual_growth_rate); // Add this line for annual growth rate
    setValue('interest_rate', house.interest_rate); // Add this line for interest rate
    setValue('monthly_payment', house.monthly_payment); // Add this line for monthly payment
    setValue('payments_made', house.payments_made); // Add this line for payments made
    setValue('number_of_payments', house.number_of_payments); // Add this line for number of payments
    setValue('sell_house', house.sell_house); // Add this line for sell house checkbox

    // Populate KIDS_ACTIVITIES -> BASEBALL
    const baseball = KIDS_ACTIVITIES.BASEBALL || {};
    setValue('baseballTeamFeeSummer', baseball.team_fee_summer || 0); // Default to 0 if undefined
    setValue('baseballTeamFeeFall', baseball.team_fee_fall || 0);
    setValue('baseballEquipment', baseball.equipment || 0);
    setValue('baseballClothing', baseball.clothing || 0);
    setValue('baseballGas', baseball.gas || 0);
    setValue('baseballGameEntry', baseball.game_entry || 0);
    setValue('baseballTravelHousing', baseball.travel_housing || 0);

    // Populate KIDS_ACTIVITIES -> SKI_TEAM
    const skiTeam = KIDS_ACTIVITIES.SKI_TEAM || {};
    setValue('skiTeamFee', skiTeam.team_fee || 0);
    setValue('skiTeamEquipment', skiTeam.equipment || 0);
    setValue('skiTeamClothing', skiTeam.clothing || 0);
    setValue('skiTeamLiftPasses', skiTeam.lift_passes || 0);
    setValue('skiTeamGas', skiTeam.gas || 0);
    setValue('skiTeamTravelHousing', skiTeam.travel_housing || 0);
    setValue('totalSkiCamp', skiTeam.Total_ski_camp || 0); // Populate total if applicable

    // Populate KIDS_ACTIVITIES -> OTHER
    const other = KIDS_ACTIVITIES.OTHER || {};
    setValue('totalCampWidji', other.total_campwidji || 0);
    setValue('jiujitsu', other.jiujitsu || 0);
    
     // New house details
     if (new_house) {
        setValue('newHouseDescription', new_house.description);
        setValue('newHouseCostBasis', new_house.cost_basis);
        setValue('newHouseClosingCosts', new_house.closing_costs);
        setValue('newHouseHomeImprovement', new_house.home_improvement);
        setValue('newHouseValue', new_house.value);
        setValue('newHouseMortgagePrincipal', new_house.mortgage_principal);
        setValue('newHouseCommissionRate', new_house.commission_rate);
        setValue('newHouseAnnualGrowthRate', new_house.annual_growth_rate);
        setValue('newHouseInterestRate', new_house.interest_rate);
        setValue('newHouseMonthlyPayment', new_house.monthly_payment);
        setValue('newHousePaymentsMade', new_house.payments_made);
        setValue('newHouseNumberOfPayments', new_house.number_of_payments);
    } else {
        // Clear new house fields if not applicable
        setValue('newHouseDescription');
        setValue('newHouseCostBasis');
        setValue('newHouseClosingCosts');
        setValue('newHouseHomeImprovement');
        setValue('newHouseValue');
        setValue('newHouseMortgagePrincipal');
        setValue('newHouseCommissionRate');
        setValue('newHouseAnnualGrowthRate');
        setValue('newHouseInterestRate');
        setValue('newHouseMonthlyPayment');
        setValue('newHousePaymentsMade');
        setValue('newHouseNumberOfPayments');
    }

    // At the end of your populateForm function
    
    setValue('investmentBalance', investment_balance);
    setValue('retirementPrincipal', retirement_principal);
    setValue('initialContribution', initial_contribution);
    setValue('increaseContribution', increase_contribution);
    setValue('employeeStockPP', employee_stock_purchase);
    
    const container = document.getElementById('genericInvestmentsContainer');
    if (container) {
        populateGenericInvestments(investment);
    } else {
        console.error("genericInvestmentsContainer not found!");
    }

    // Create education sections for each child
    children.forEach(child => {
        createEducationSection(child.name, child, `${child.name.toLowerCase()}Education`);
    });

    createGainsInputs(gains);

        // Populate Retirement Data for Spouse 1 and Spouse 2
        if (RETIREMENT.length > 0) {
            // Spouse 1
            const spouse1 = RETIREMENT.find(spouse => spouse.name === 'Spouse 1');
            if (spouse1) {
                // Contributions
                setValue('spouse1_roth_posttax', spouse1.contributions.Roth[0].spouse1_retirement_contribution_posttax);
                setValue('spouse1_employer_match', spouse1.contributions['401K'][0].Spouse1_Employer_Match);
                setValue('spouse1_pretax_401k', spouse1.contributions['401K'][1].spouse1_retirement_contribution_pretax);
    
                // Accounts
                setValue('spouse1_roth_ira', spouse1.accounts.Roth[0]['Roth IRA']);
                setValue('spouse1_traditional_ira', spouse1.accounts.IRA[0].Traditional);
                setValue('spouse1_401k', spouse1.accounts['401K'][0]['401k']);
                setValue('spouse1_rollover_401k', spouse1.accounts['401K'][2]['Rollover 401K']);
            }
    
            // Spouse 2
            const spouse2 = RETIREMENT.find(spouse => spouse.name === 'Spouse 2');
            if (spouse2) {
                // Contributions
                setValue('spouse2_roth_posttax', spouse2.contributions.Roth[0].spouse2_retirement_contribution_posttax);
                setValue('spouse2_employer_match', spouse2.contributions['401K'][0].Spouse2_Employer_Match);
                setValue('spouse2_pretax_401k', spouse2.contributions['401K'][1].spouse2_retirement_contribution_pretax);
    
                // Accounts
                setValue('spouse2_roth_ira', spouse2.accounts.Roth[0]['Roth IRA']);
                setValue('spouse2_traditional_ira', spouse2.accounts.IRA[0]['Traditional IRA']);
                setValue('spouse2_rollover_ira', spouse2.accounts.IRA[1]['Rollover IRA']);
                setValue('spouse2_401k', spouse2.accounts['401K'][0]['401k']);
            }
        }
}

let investmentCount = 0; // Initialize a counter for unique investment IDs

function populateGenericInvestments(investments) {
    const investmentsContainer = document.getElementById('genericInvestmentsContainer');

    // Clear existing investments
    investmentsContainer.innerHTML = '';
    investmentCount = 0; // Reset the counter

    // Iterate through the investments object
    for (const key in investments) {
        if (investments.hasOwnProperty(key)) {
            const investment = investments[key];

            // Create a new div for the investment
            investmentCount++; // Increment the count for unique ID

            const investmentDiv = document.createElement('div');
            investmentDiv.classList.add('genericInvestment');
            investmentDiv.id = `genericInvestment${investmentCount}`; // Generate unique ID

            const investmentWrapper = document.createElement('div');
            investmentWrapper.classList.add('two-column');

            // Name input group
            const nameGroup = document.createElement('div');
            nameGroup.classList.add('form-group');

            const nameLabel = document.createElement('label');
            nameLabel.setAttribute('for', investmentDiv.id + 'Name');
            nameLabel.textContent = `Investment Name ${investmentCount}:`;
            nameGroup.appendChild(nameLabel);

            const nameInput = document.createElement('input');
            nameInput.type = 'text';
            nameInput.id = investmentDiv.id + 'Name';
            nameInput.name = `genericInvestmentName${investmentCount}`;
            nameInput.value = investment.name || ''; // Set the name
            nameGroup.appendChild(nameInput);

            // Value input group
            const valueGroup = document.createElement('div');
            valueGroup.classList.add('form-group');

            const valueLabel = document.createElement('label');
            valueLabel.setAttribute('for', investmentDiv.id + 'Value');
            valueLabel.textContent = `Investment Value ${investmentCount}:`;
            valueGroup.appendChild(valueLabel);

            const valueInput = document.createElement('input');
            valueInput.type = 'number';
            valueInput.id = investmentDiv.id + 'Value';
            valueInput.name = `genericInvestmentValue${investmentCount}`;
            valueInput.value = investment.amount || ''; // Set the value
            valueInput.step = "0.01";
            valueGroup.appendChild(valueInput);

            // Append the input groups to the investment wrapper
            investmentWrapper.appendChild(nameGroup);
            investmentWrapper.appendChild(valueGroup);
            investmentDiv.appendChild(investmentWrapper);

            // Append investment div to the container
            investmentsContainer.appendChild(investmentDiv);
        }
    }
}



// Function to add a new investment
function addInvestment() {
    const investmentsContainer = document.getElementById('genericInvestmentsContainer');
    investmentCount++; // Increment the count for unique ID

    // Create a new div for the investment
    const investmentDiv = document.createElement('div');
    investmentDiv.classList.add('genericInvestment');
    investmentDiv.id = `genericInvestment${investmentCount}`; // Generate unique ID

    const nameLabel = document.createElement('label');
    nameLabel.setAttribute('for', investmentDiv.id + 'Name');
    nameLabel.textContent = `Investment Name ${investmentCount}:`;
    investmentDiv.appendChild(nameLabel);

    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.id = investmentDiv.id + 'Name';
    nameInput.name = `genericInvestmentName${investmentCount}`;
    investmentDiv.appendChild(nameInput);

    const valueLabel = document.createElement('label');
    valueLabel.setAttribute('for', investmentDiv.id + 'Value');
    valueLabel.textContent = `Investment Value ${investmentCount}:`;
    investmentDiv.appendChild(valueLabel);

    const valueInput = document.createElement('input');
    valueInput.type = 'number';
    valueInput.id = investmentDiv.id + 'Value';
    valueInput.name = `genericInvestmentValue${investmentCount}`;
    valueInput.step = "0.01";
    investmentDiv.appendChild(valueInput);

    // Append the new investment div to the container
    investmentsContainer.appendChild(investmentDiv);
}


async function loadGeneralFinance() {
    try {
        const response = await fetch('/static/scenarios/general.finance.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error loading general finance data:', error);
        return {};
    }
}

async function loadScenario(scenarioFile) {
    const generalFinance = await loadGeneralFinance();
    
    try {
        const response = await fetch(`/scenarios/${scenarioFile}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const scenarioData = await response.json();

        // Merge general finance data with scenario data
        const combinedData = { ...generalFinance, ...scenarioData };
        populateForm(combinedData);
    } catch (error) {
        console.error('Error loading scenario data:', error);
    }
}

// Example utility function to set values and create form fields
function createYearInputField(childName, schoolType, year, cost) {
    const div = document.createElement('div');
    div.classList.add('form-group');
    
    const label = document.createElement('label');
    label.for = `${childName}${schoolType}${year}`;
    label.textContent = `${year}:`;
    
    const input = document.createElement('input');
    input.type = 'number';
    input.id = `${childName}${schoolType}${year}`;
    input.name = `${childName}_${schoolType}_${year}`;
    input.placeholder = `Enter cost for ${year}`;
    input.value = cost || '';
    
    div.appendChild(label);
    div.appendChild(input);
    return div;
}

// Function to dynamically generate form fields for high school and college expenses
function createEducationSection(childName, childData, sectionId) {
    // Find the container where the education fields will be added
    const section = document.getElementById(sectionId);
    if (!section) return;

    // Clear previous content (if any)
    section.innerHTML = '';

    // Create High School Expense Fields
    const highSchoolSection = document.createElement('div');
    highSchoolSection.innerHTML = `<h3>${childName} - High School Expenses</h3>`;
    
    // Create a div for two columns layout
    const highSchoolDiv = document.createElement('div');
    highSchoolDiv.className = 'two-column';

    childData.school.high_school.forEach(({ year, cost }) => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        const label = document.createElement('label');
        label.textContent = `Year ${year}:`;
        label.setAttribute('for', `${childName.toLowerCase()}_highschool_${year}`);

        const input = document.createElement('input');
        input.type = 'number';
        input.id = `${childName.toLowerCase()}_highschool_${year}`;
        input.name = `${childName.toLowerCase()}_highschool_${year}`; // Optional, if you want to identify input fields
        input.placeholder = 'Enter high school cost';
        input.required = true; // Set required attribute as needed
        input.value = cost || ''; // Default to empty if cost is not provided

        // Append label and input to the form group
        formGroup.appendChild(label);
        formGroup.appendChild(input);
        
        // Append form group to high school div
        highSchoolDiv.appendChild(formGroup);
    });
    highSchoolSection.appendChild(highSchoolDiv);
    section.appendChild(highSchoolSection);

    // Create College Expense Fields
    const collegeSection = document.createElement('div');
    collegeSection.innerHTML = `<h3>${childName} - College Expenses</h3>`;
    
    // Create a div for two columns layout
    const collegeDiv = document.createElement('div');
    collegeDiv.className = 'two-column';

    childData.school.college.forEach(({ year, cost }) => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        const label = document.createElement('label');
        label.textContent = `Year ${year}:`;
        label.setAttribute('for', `${childName.toLowerCase()}_college_${year}`);

        const input = document.createElement('input');
        input.type = 'number';
        input.id = `${childName.toLowerCase()}_college_${year}`;
        input.name = `${childName.toLowerCase()}_college_${year}`; // Optional, if you want to identify input fields
        input.placeholder = 'Enter college cost';
        input.required = true; // Set required attribute as needed
        input.value = cost || ''; // Default to empty if cost is not provided

        // Append label and input to the form group
        formGroup.appendChild(label);
        formGroup.appendChild(input);
        
        // Append form group to college div
        collegeDiv.appendChild(formGroup);
    });
    collegeSection.appendChild(collegeDiv);
    section.appendChild(collegeSection);
}

// Function to generate input fields for each year
function createGainsInputs(gains) {
    const gainsContainer = document.getElementById('gainsContainer');
    gainsContainer.innerHTML = ''; // Clear any existing inputs

    gains.forEach((gain, index) => {
        const inputDiv = document.createElement('div');
        inputDiv.className = 'year-input';

        // Create a unique id for each input field
        const inputId = `gainYear${index + 1}`;

        const label = document.createElement('label');
        label.setAttribute('for', inputId); // Associate the label with the input field
        label.textContent = `Year ${index + 1} Gain:`; // Adjust label text for clarity
        inputDiv.appendChild(label);

        const input = document.createElement('input');
        input.type = 'number';
        input.value = gain;
        input.id = inputId; // Set the id for the input field
        input.name = `gainYear${index + 1}`; // Set a name for the input
        input.required = true; // Optional: make it required

        inputDiv.appendChild(input);
        gainsContainer.appendChild(inputDiv);
    });
}
