// Translation system for Hindi and English
const translations = {
    en: {
        // Navigation
        'nav.home': 'Home',
        'nav.login': 'Login',
        'nav.signup': 'Sign Up',
        'nav.about': 'About Us',
        'nav.share': 'Share',
        'nav.logout': 'Logout',
        'nav.profileSettings': 'Profile Settings',
        'nav.accountSettings': 'Account Settings',
        'nav.myListings': 'My Listings',
        'nav.shareApp': 'Share App',
        
        // Common
        'common.cancel': 'Cancel',
        'common.save': 'Save',
        'common.submit': 'Submit',
        'common.delete': 'Delete',
        'common.edit': 'Edit',
        'common.close': 'Close',
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.success': 'Success',
        
        // Landing Page
        'landing.heroTitle': 'Welcome to Farming App',
        'landing.heroSubtitle': 'Revolutionize your farming operations with our comprehensive agricultural management platform. Manage your farming processes efficiently and digitally.',
        'landing.getStarted': 'Get Started',
        'landing.learnMore': 'Learn More',
        'landing.digitalManagement': 'Digital Management',
        'landing.digitalManagementDesc': 'Comprehensive digital management system for your farming operations. Track and manage all your agricultural processes efficiently.',
        'landing.mobileAccess': 'Mobile Access',
        'landing.mobileAccessDesc': 'Quick and secure mobile access system. Streamline your farm operations with modern technology.',
        'landing.analytics': 'Analytics',
        'landing.analyticsDesc': 'Comprehensive analytics and reporting. Make data-driven decisions for your farming business.',
        'landing.ctaTitle': 'Ready to Transform Your Farming?',
        'landing.ctaSubtitle': 'Join thousands of farmers who are already using our platform to optimize their operations.',
        'landing.createAccount': 'Create Account',
        'landing.signIn': 'Sign In',
        
        // Login Page
        'login.title': 'Login',
        'login.email': 'Email Address',
        'login.emailPlaceholder': 'Enter your email',
        'login.password': 'Password',
        'login.passwordPlaceholder': 'Enter your password',
        'login.submit': 'Login to Farming App',
        'login.noAccount': "Don't have an account?",
        'login.signUp': 'Sign Up',
        
        // Signup Page
        'signup.title': 'Sign Up',
        'signup.name': 'Full Name',
        'signup.namePlaceholder': 'Enter your full name',
        'signup.email': 'Email Address',
        'signup.emailPlaceholder': 'Enter your email',
        'signup.password': 'Password',
        'signup.passwordPlaceholder': 'Enter your password',
        'signup.confirmPassword': 'Confirm Password',
        'signup.confirmPasswordPlaceholder': 'Confirm your password',
        'signup.submit': 'Create Account',
        'signup.haveAccount': 'Already have an account?',
        'signup.login': 'Login',
        
        // Profile
        'profile.fullName': 'Full Name',
        'profile.email': 'Email Address',
        'profile.phone': 'Phone Number',
        'profile.location': 'Farm Location',
        'profile.bio': 'Bio',
        'profile.bioPlaceholder': 'Tell us about your farming experience...',
        'profile.saveChanges': 'Save Changes',
        'profile.currentPassword': 'Current Password',
        'profile.newPassword': 'New Password',
        'profile.confirmNewPassword': 'Confirm New Password',
        'profile.updatePassword': 'Update Password',
        'profile.totalListings': 'Total Listings',
        'profile.active': 'Active',
        'profile.totalValue': 'Total Value',
        
        // Market
        'market.title': 'Market Updates',
        'market.price': 'Price',
        'market.quantity': 'Quantity',
        'market.location': 'Location',
        'market.category': 'Category',
        
        // Sell
        'sell.title': 'Sell Crops',
        'sell.cropName': 'Crop Name',
        'sell.quantity': 'Quantity',
        'sell.price': 'Price per Unit',
        'sell.location': 'Location',
        'sell.description': 'Description',
        
        // Buy
        'buy.title': 'Buy Crops',
        'buy.subtitle': 'Find and purchase fresh crops from local farmers',
        'buy.search': 'Search crops to buy...',
        'buy.filter': 'Filter',
        'buy.category': 'Category:',
        'buy.allCrops': 'All Crops',
        'buy.priceRange': 'Price Range:',
        'buy.anyPrice': 'Any Price',
        'buy.location': 'Location:',
        'buy.allLocations': 'All Locations',
        'buy.applyFilters': 'Apply Filters',
        'buy.availableCrops': 'Available Crops',
        'buy.by': 'By:',
        'buy.kgAvailable': 'kg available',
        'buy.listed': 'Listed:',
        'buy.recentlyListed': 'Recently listed',
        'buy.total': 'Total:',
        'buy.edit': 'Edit',
        'buy.delete': 'Delete',
        'buy.contactSeller': 'Contact Seller',
        'buy.buyNow': 'Buy Now',
        'buy.yourListing': 'Your Listing',
        'buy.noCrops': 'No crops available',
        'buy.checkBack': 'Check back later for new crop listings!',
        'buy.grains': 'Grains',
        'buy.vegetables': 'Vegetables',
        'buy.fruits': 'Fruits',
        'buy.spices': 'Spices',
        
        // Sell
        'sell.title': 'Sell Your Crops',
        'sell.subtitle': 'List your harvest and connect with buyers',
        'sell.search': 'Search your listings...',
        'sell.listCrop': 'List Your Crop',
        'sell.sellHarvest': 'Sell Your Harvest',
        'sell.cropName': 'Crop Name',
        'sell.cropNamePlaceholder': 'Enter crop name',
        'sell.category': 'Category',
        'sell.selectCategory': 'Select Category',
        'sell.quantity': 'Quantity (kg)',
        'sell.quantityPlaceholder': 'Enter quantity',
        'sell.price': 'Price per kg (₹)',
        'sell.pricePlaceholder': 'Enter price per kg',
        'sell.farmLocation': 'Farm Location',
        'sell.locationPlaceholder': 'Enter your farm location',
        'sell.description': 'Description',
        'sell.descriptionPlaceholder': 'Describe your crop quality, organic status, etc.',
        'sell.listMyCrop': 'List My Crop',
        'sell.myActiveListings': 'My Active Listings',
        'sell.categoryLabel': 'Category:',
        'sell.quantityLabel': 'Quantity:',
        'sell.priceLabel': 'Price:',
        'sell.totalValue': 'Total Value:',
        'sell.locationLabel': 'Location:',
        'sell.listedLabel': 'Listed:',
        'sell.recently': 'Recently',
        'sell.active': 'Active',
        'sell.inactive': 'Inactive',
        'sell.noListings': 'No listings yet',
        'sell.createFirst': 'Create your first crop listing using the form above!',
        
        // Market
        'market.title': 'Market Updates',
        'market.subtitle': 'Stay informed with latest agricultural market trends',
        'market.search': 'Search market news...',
        'market.wheatPrice': 'Wheat Price',
        'market.cornPrice': 'Corn Price',
        'market.tomatoPrice': 'Tomato Price',
        'market.carrotPrice': 'Carrot Price',
        'market.latestNews': 'Latest Market News',
        'market.refresh': 'Refresh',
        'market.refreshing': 'Refreshing...',
        'market.positiveImpact': 'Positive Impact',
        'market.negativeImpact': 'Negative Impact',
        'market.neutralImpact': 'Neutral Impact',
        'market.source': 'Source:',
        'market.unknownTime': 'Unknown time',
        'market.analysis': 'Market Analysis',
        'market.priceTrends': 'Price Trends',
        'market.demandForecast': 'Demand Forecast',
        'market.highDemand': 'High Demand',
        'market.stable': 'Stable',
        'market.growing': 'Growing',
        'market.addUpdate': 'Add Market Update',
        'market.updateTitle': 'Update Title',
        'market.updateTitlePlaceholder': 'Enter update title',
        'market.updateCategory': 'Category',
        'market.selectCategory': 'Select Category',
        'market.priceUpdate': 'Price Update',
        'market.weatherImpact': 'Weather Impact',
        'market.demandSupply': 'Demand & Supply',
        'market.governmentPolicy': 'Government Policy',
        'market.technology': 'Technology',
        'market.exportImport': 'Export/Import',
        'market.other': 'Other',
        'market.description': 'Description',
        'market.descriptionPlaceholder': 'Describe the market update in detail...',
        'market.marketImpact': 'Market Impact',
        'market.sourceOptional': 'Source (Optional)',
        'market.sourcePlaceholder': 'e.g., Government Report, News Agency',
        'market.addUpdateBtn': 'Add Update',
        
        // Signup
        'signup.title': 'Sign Up',
        'signup.phone': 'Phone Number',
        'signup.phonePlaceholder': 'Enter your phone number',
        'signup.confirmPassword': 'Confirm Password',
        'signup.confirmPasswordPlaceholder': 'Confirm your password',
        'signup.createPassword': 'Create a strong password',
        'signup.submit': 'Join Farming Community',
        'signup.haveAccount': 'Already have an account?',
        'signup.login': 'Login',
        
        // Action Buttons
        'actions.marketUpdates': 'Market Updates',
        'actions.sellCrops': 'Sell Crops',
        'actions.buyCrops': 'Buy Crops',
        
        // Chatbot
        'chatbot.title': 'Farming Assistant',
        'chatbot.online': 'Online',
        'chatbot.placeholder': 'Ask me about farming, crops, or the app...',
        
        // About
        'about.title': 'About Us',
        
        // App Brand
        'app.brand': 'Farming App',
        'app.tagline': 'Agricultural Management Platform'
    },
    hi: {
        // Navigation
        'nav.home': 'होम',
        'nav.login': 'लॉगिन',
        'nav.signup': 'साइन अप',
        'nav.about': 'हमारे बारे में',
        'nav.share': 'साझा करें',
        'nav.logout': 'लॉगआउट',
        'nav.profileSettings': 'प्रोफ़ाइल सेटिंग्स',
        'nav.accountSettings': 'खाता सेटिंग्स',
        'nav.myListings': 'मेरी सूचियां',
        'nav.shareApp': 'ऐप साझा करें',
        
        // Common
        'common.cancel': 'रद्द करें',
        'common.save': 'सहेजें',
        'common.submit': 'जमा करें',
        'common.delete': 'हटाएं',
        'common.edit': 'संपादित करें',
        'common.close': 'बंद करें',
        'common.loading': 'लोड हो रहा है...',
        'common.error': 'त्रुटि',
        'common.success': 'सफलता',
        
        // Landing Page
        'landing.heroTitle': 'फार्मिंग ऐप में आपका स्वागत है',
        'landing.heroSubtitle': 'हमारे व्यापक कृषि प्रबंधन प्लेटफॉर्म के साथ अपने कृषि संचालन में क्रांति लाएं। अपनी कृषि प्रक्रियाओं को कुशलतापूर्वक और डिजिटल रूप से प्रबंधित करें।',
        'landing.getStarted': 'शुरू करें',
        'landing.learnMore': 'अधिक जानें',
        'landing.digitalManagement': 'डिजिटल प्रबंधन',
        'landing.digitalManagementDesc': 'आपके कृषि संचालन के लिए व्यापक डिजिटल प्रबंधन प्रणाली। अपनी सभी कृषि प्रक्रियाओं को कुशलतापूर्वक ट्रैक और प्रबंधित करें।',
        'landing.mobileAccess': 'मोबाइल एक्सेस',
        'landing.mobileAccessDesc': 'त्वरित और सुरक्षित मोबाइल एक्सेस प्रणाली। आधुनिक तकनीक के साथ अपने फार्म संचालन को सुव्यवस्थित करें।',
        'landing.analytics': 'विश्लेषण',
        'landing.analyticsDesc': 'व्यापक विश्लेषण और रिपोर्टिंग। अपने कृषि व्यवसाय के लिए डेटा-संचालित निर्णय लें।',
        'landing.ctaTitle': 'अपनी कृषि को बदलने के लिए तैयार हैं?',
        'landing.ctaSubtitle': 'हजारों किसानों में शामिल हों जो पहले से ही अपने संचालन को अनुकूलित करने के लिए हमारे प्लेटफॉर्म का उपयोग कर रहे हैं।',
        'landing.createAccount': 'खाता बनाएं',
        'landing.signIn': 'साइन इन करें',
        
        // Login Page
        'login.title': 'लॉगिन',
        'login.email': 'ईमेल पता',
        'login.emailPlaceholder': 'अपना ईमेल दर्ज करें',
        'login.password': 'पासवर्ड',
        'login.passwordPlaceholder': 'अपना पासवर्ड दर्ज करें',
        'login.submit': 'फार्मिंग ऐप में लॉगिन करें',
        'login.noAccount': 'खाता नहीं है?',
        'login.signUp': 'साइन अप करें',
        
        // Signup Page
        'signup.title': 'साइन अप',
        'signup.name': 'पूरा नाम',
        'signup.namePlaceholder': 'अपना पूरा नाम दर्ज करें',
        'signup.email': 'ईमेल पता',
        'signup.emailPlaceholder': 'अपना ईमेल दर्ज करें',
        'signup.password': 'पासवर्ड',
        'signup.passwordPlaceholder': 'अपना पासवर्ड दर्ज करें',
        'signup.confirmPassword': 'पासवर्ड की पुष्टि करें',
        'signup.confirmPasswordPlaceholder': 'अपने पासवर्ड की पुष्टि करें',
        'signup.submit': 'खाता बनाएं',
        'signup.haveAccount': 'पहले से खाता है?',
        'signup.login': 'लॉगिन',
        
        // Profile
        'profile.fullName': 'पूरा नाम',
        'profile.email': 'ईमेल पता',
        'profile.phone': 'फोन नंबर',
        'profile.location': 'फार्म स्थान',
        'profile.bio': 'जीवनी',
        'profile.bioPlaceholder': 'हमें अपने कृषि अनुभव के बारे में बताएं...',
        'profile.saveChanges': 'परिवर्तन सहेजें',
        'profile.currentPassword': 'वर्तमान पासवर्ड',
        'profile.newPassword': 'नया पासवर्ड',
        'profile.confirmNewPassword': 'नए पासवर्ड की पुष्टि करें',
        'profile.updatePassword': 'पासवर्ड अपडेट करें',
        'profile.totalListings': 'कुल सूचियां',
        'profile.active': 'सक्रिय',
        'profile.totalValue': 'कुल मूल्य',
        
        // Market
        'market.title': 'बाजार अपडेट',
        'market.price': 'मूल्य',
        'market.quantity': 'मात्रा',
        'market.location': 'स्थान',
        'market.category': 'श्रेणी',
        
        // Sell
        'sell.title': 'फसलें बेचें',
        'sell.cropName': 'फसल का नाम',
        'sell.quantity': 'मात्रा',
        'sell.price': 'प्रति यूनिट मूल्य',
        'sell.location': 'स्थान',
        'sell.description': 'विवरण',
        
        // Buy
        'buy.title': 'फसलें खरीदें',
        'buy.subtitle': 'स्थानीय किसानों से ताजी फसलें खोजें और खरीदें',
        'buy.search': 'खरीदने के लिए फसलें खोजें...',
        'buy.filter': 'फ़िल्टर',
        'buy.category': 'श्रेणी:',
        'buy.allCrops': 'सभी फसलें',
        'buy.priceRange': 'मूल्य सीमा:',
        'buy.anyPrice': 'कोई मूल्य',
        'buy.location': 'स्थान:',
        'buy.allLocations': 'सभी स्थान',
        'buy.applyFilters': 'फ़िल्टर लागू करें',
        'buy.availableCrops': 'उपलब्ध फसलें',
        'buy.by': 'द्वारा:',
        'buy.kgAvailable': 'किलो उपलब्ध',
        'buy.listed': 'सूचीबद्ध:',
        'buy.recentlyListed': 'हाल ही में सूचीबद्ध',
        'buy.total': 'कुल:',
        'buy.edit': 'संपादित करें',
        'buy.delete': 'हटाएं',
        'buy.contactSeller': 'विक्रेता से संपर्क करें',
        'buy.buyNow': 'अभी खरीदें',
        'buy.yourListing': 'आपकी सूची',
        'buy.noCrops': 'कोई फसल उपलब्ध नहीं',
        'buy.checkBack': 'नई फसल सूचियों के लिए बाद में वापस जांचें!',
        'buy.grains': 'अनाज',
        'buy.vegetables': 'सब्जियां',
        'buy.fruits': 'फल',
        'buy.spices': 'मसाले',
        
        // Sell
        'sell.title': 'अपनी फसलें बेचें',
        'sell.subtitle': 'अपनी फसल सूचीबद्ध करें और खरीदारों से जुड़ें',
        'sell.search': 'अपनी सूचियां खोजें...',
        'sell.listCrop': 'अपनी फसल सूचीबद्ध करें',
        'sell.sellHarvest': 'अपनी फसल बेचें',
        'sell.cropName': 'फसल का नाम',
        'sell.cropNamePlaceholder': 'फसल का नाम दर्ज करें',
        'sell.category': 'श्रेणी',
        'sell.selectCategory': 'श्रेणी चुनें',
        'sell.quantity': 'मात्रा (किलो)',
        'sell.quantityPlaceholder': 'मात्रा दर्ज करें',
        'sell.price': 'प्रति किलो मूल्य (₹)',
        'sell.pricePlaceholder': 'प्रति किलो मूल्य दर्ज करें',
        'sell.farmLocation': 'फार्म स्थान',
        'sell.locationPlaceholder': 'अपना फार्म स्थान दर्ज करें',
        'sell.description': 'विवरण',
        'sell.descriptionPlaceholder': 'अपनी फसल की गुणवत्ता, जैविक स्थिति आदि का वर्णन करें',
        'sell.listMyCrop': 'मेरी फसल सूचीबद्ध करें',
        'sell.myActiveListings': 'मेरी सक्रिय सूचियां',
        'sell.categoryLabel': 'श्रेणी:',
        'sell.quantityLabel': 'मात्रा:',
        'sell.priceLabel': 'मूल्य:',
        'sell.totalValue': 'कुल मूल्य:',
        'sell.locationLabel': 'स्थान:',
        'sell.listedLabel': 'सूचीबद्ध:',
        'sell.recently': 'हाल ही में',
        'sell.active': 'सक्रिय',
        'sell.inactive': 'निष्क्रिय',
        'sell.noListings': 'अभी तक कोई सूची नहीं',
        'sell.createFirst': 'ऊपर दिए गए फॉर्म का उपयोग करके अपनी पहली फसल सूची बनाएं!',
        
        // Market
        'market.title': 'बाजार अपडेट',
        'market.subtitle': 'नवीनतम कृषि बाजार रुझानों से सूचित रहें',
        'market.search': 'बाजार समाचार खोजें...',
        'market.wheatPrice': 'गेहूं मूल्य',
        'market.cornPrice': 'मक्का मूल्य',
        'market.tomatoPrice': 'टमाटर मूल्य',
        'market.carrotPrice': 'गाजर मूल्य',
        'market.latestNews': 'नवीनतम बाजार समाचार',
        'market.refresh': 'ताज़ा करें',
        'market.refreshing': 'ताज़ा हो रहा है...',
        'market.positiveImpact': 'सकारात्मक प्रभाव',
        'market.negativeImpact': 'नकारात्मक प्रभाव',
        'market.neutralImpact': 'तटस्थ प्रभाव',
        'market.source': 'स्रोत:',
        'market.unknownTime': 'अज्ञात समय',
        'market.analysis': 'बाजार विश्लेषण',
        'market.priceTrends': 'मूल्य रुझान',
        'market.demandForecast': 'मांग पूर्वानुमान',
        'market.highDemand': 'उच्च मांग',
        'market.stable': 'स्थिर',
        'market.growing': 'बढ़ रहा है',
        'market.addUpdate': 'बाजार अपडेट जोड़ें',
        'market.updateTitle': 'अपडेट शीर्षक',
        'market.updateTitlePlaceholder': 'अपडेट शीर्षक दर्ज करें',
        'market.updateCategory': 'श्रेणी',
        'market.selectCategory': 'श्रेणी चुनें',
        'market.priceUpdate': 'मूल्य अपडेट',
        'market.weatherImpact': 'मौसम प्रभाव',
        'market.demandSupply': 'मांग और आपूर्ति',
        'market.governmentPolicy': 'सरकारी नीति',
        'market.technology': 'प्रौद्योगिकी',
        'market.exportImport': 'निर्यात/आयात',
        'market.other': 'अन्य',
        'market.description': 'विवरण',
        'market.descriptionPlaceholder': 'बाजार अपडेट का विस्तार से वर्णन करें...',
        'market.marketImpact': 'बाजार प्रभाव',
        'market.sourceOptional': 'स्रोत (वैकल्पिक)',
        'market.sourcePlaceholder': 'उदा., सरकारी रिपोर्ट, समाचार एजेंसी',
        'market.addUpdateBtn': 'अपडेट जोड़ें',
        
        // Signup
        'signup.phone': 'फोन नंबर',
        'signup.phonePlaceholder': 'अपना फोन नंबर दर्ज करें',
        'signup.createPassword': 'एक मजबूत पासवर्ड बनाएं',
        'signup.submit': 'कृषि समुदाय में शामिल हों',
        
        // Action Buttons
        'actions.marketUpdates': 'बाजार अपडेट',
        'actions.sellCrops': 'फसलें बेचें',
        'actions.buyCrops': 'फसलें खरीदें',
        
        // Chatbot
        'chatbot.title': 'कृषि सहायक',
        'chatbot.online': 'ऑनलाइन',
        'chatbot.placeholder': 'मुझसे कृषि, फसलों, या ऐप के बारे में पूछें...',
        
        // About
        'about.title': 'हमारे बारे में',
        
        // App Brand
        'app.brand': 'फार्मिंग ऐप',
        'app.tagline': 'कृषि प्रबंधन प्लेटफॉर्म'
    }
};

// Current language (default: English)
let currentLanguage = localStorage.getItem('appLanguage') || 'en';

// Translation function
function t(key) {
    return translations[currentLanguage][key] || translations['en'][key] || key;
}

// Set language
function setLanguage(lang) {
    if (translations[lang]) {
        currentLanguage = lang;
        localStorage.setItem('appLanguage', lang);
        translatePage();
        updateLanguageButton();
    }
}

// Toggle language
function toggleLanguage() {
    const newLang = currentLanguage === 'en' ? 'hi' : 'en';
    setLanguage(newLang);
}

// Update language button text
function updateLanguageButton() {
    const langBtn = document.getElementById('lang-toggle-btn');
    if (langBtn) {
        langBtn.textContent = currentLanguage === 'en' ? 'हिंदी' : 'English';
        langBtn.setAttribute('title', currentLanguage === 'en' ? 'Switch to Hindi' : 'हिंदी से अंग्रेजी में बदलें');
    }
}

// Translate page content
function translatePage() {
    // Translate elements with data-translate attribute
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        const translation = t(key);
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            // Only update placeholder if it's a placeholder attribute
            if (element.hasAttribute('placeholder') || element.getAttribute('data-translate').includes('Placeholder')) {
                element.placeholder = translation;
            } else {
                element.value = translation;
            }
        } else if (element.tagName === 'OPTION') {
            // For select options, update text content
            element.textContent = translation;
        } else if (element.tagName === 'BUTTON' || element.tagName === 'A') {
            // For buttons and links, preserve emojis if present
            const originalText = element.textContent;
            // Extended emoji regex to include all emojis used in the app
            const emojiMatch = originalText.match(/[🚀📖🌱📤⚙️👤📊🚪🛒🌾📈🌽🍅🥕💬🔄📉➡️✏️🗑️👤]/);
            if (emojiMatch) {
                element.innerHTML = `${emojiMatch[0]} ${translation}`;
            } else {
                element.textContent = translation;
            }
        } else {
            // For other elements, check if they contain emojis
            const originalHTML = element.innerHTML;
            // Extended emoji regex to include all emojis used in the app
            const emojiMatch = originalHTML.match(/[🚀📖🌱📤⚙️👤📊🚪🛒🌾📈🌽🍅🥕💬🔄📉➡️✏️🗑️👤]/);
            // Special handling for page headers with emojis
            if (element.tagName === 'H1' && (key === 'buy.title' || key === 'sell.title' || key === 'market.title')) {
                const emoji = key === 'buy.title' ? '🛒' : key === 'sell.title' ? '🌾' : '📊';
                element.innerHTML = `${emoji} ${translation}`;
            } else if (element.tagName === 'H2' && (key === 'market.latestNews' || key === 'market.analysis')) {
                // Special handling for H2 headings with emojis
                const emoji = key === 'market.latestNews' ? '📈' : '📊';
                element.innerHTML = `${emoji} ${translation}`;
            } else if (emojiMatch && !originalHTML.includes('<span') && !originalHTML.includes('<div')) {
                element.innerHTML = `${emojiMatch[0]} ${translation}`;
            } else {
                // If element has child elements with data-translate, don't replace innerHTML
                const hasTranslatableChildren = element.querySelector('[data-translate]');
                if (!hasTranslatableChildren) {
                    element.textContent = translation;
                }
            }
        }
    });
    
    // Translate navigation
    translateNavigation();
    
    // Translate modals
    translateModals();
    
    // Translate page-specific content
    translatePageContent();
    
    // Update HTML lang attribute
    document.documentElement.lang = currentLanguage;
}

// Translate navigation
function translateNavigation() {
    const navLinks = {
        'nav.home': document.querySelector('a[href="/"]'),
        'nav.login': document.getElementById('login-nav-link'),
        'nav.signup': document.getElementById('signup-nav-link'),
        'nav.about': document.querySelector('a[href="/about"]'),
        'nav.logout': document.getElementById('logout-nav-link')
    };
    
    Object.keys(navLinks).forEach(key => {
        const element = navLinks[key];
        if (element) {
            element.textContent = t(key);
        }
    });
    
    // Translate brand
    const brandTitle = document.querySelector('.nav-brand h1');
    if (brandTitle) {
        brandTitle.innerHTML = `🌱 ${t('app.brand')}`;
    }
    
    const brandSubtitle = document.querySelector('.nav-brand p');
    if (brandSubtitle) {
        brandSubtitle.textContent = t('app.tagline');
    }
}

// Translate modals
function translateModals() {
    // Profile Settings Modal
    const profileModalTitle = document.querySelector('#profileModal .modal-header h2');
    if (profileModalTitle) {
        profileModalTitle.innerHTML = `👤 ${t('nav.profileSettings')}`;
    }
    
    // Account Settings Modal
    const accountModalTitle = document.querySelector('#accountModal .modal-header h2');
    if (accountModalTitle) {
        accountModalTitle.innerHTML = `⚙️ ${t('nav.accountSettings')}`;
    }
    
    // My Listings Modal
    const listingsModalTitle = document.querySelector('#listingsModal .modal-header h2');
    if (listingsModalTitle) {
        listingsModalTitle.innerHTML = `📊 ${t('nav.myListings')}`;
    }
    
    // Translate form labels and placeholders
    translateFormElements();
}

// Translate form elements
function translateFormElements() {
    // Profile form
    const profileLabels = {
        'profile-name': 'profile.fullName',
        'profile-email': 'profile.email',
        'profile-phone': 'profile.phone',
        'profile-location': 'profile.location',
        'profile-bio': 'profile.bio'
    };
    
    Object.keys(profileLabels).forEach(id => {
        const label = document.querySelector(`label[for="${id}"]`);
        const input = document.getElementById(id);
        if (label) label.textContent = t(profileLabels[id]);
        if (input && input.placeholder) {
            input.placeholder = t(profileLabels[id] + 'Placeholder') || '';
        }
    });
    
    // Account form
    const accountLabels = {
        'current-password': 'profile.currentPassword',
        'new-password': 'profile.newPassword',
        'confirm-new-password': 'profile.confirmNewPassword'
    };
    
    Object.keys(accountLabels).forEach(id => {
        const label = document.querySelector(`label[for="${id}"]`);
        const input = document.getElementById(id);
        if (label) label.textContent = t(accountLabels[id]);
        if (input && input.placeholder) {
            input.placeholder = t(accountLabels[id] + 'Placeholder') || '';
        }
    });
    
    // Buttons
    const cancelBtns = document.querySelectorAll('.btn-secondary');
    cancelBtns.forEach(btn => {
        if (btn.textContent.includes('Cancel') || btn.textContent.includes('रद्द')) {
            btn.textContent = t('common.cancel');
        }
    });
    
    const saveBtns = document.querySelectorAll('button[type="submit"]');
    saveBtns.forEach(btn => {
        if (btn.textContent.includes('Save') || btn.textContent.includes('सहेज')) {
            btn.textContent = t('common.save');
        }
    });
}

// Translate page-specific content
function translatePageContent() {
    // Landing page
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) heroTitle.textContent = t('landing.heroTitle');
    
    const heroSubtitle = document.querySelector('.hero-subtitle');
    if (heroSubtitle) heroSubtitle.textContent = t('landing.heroSubtitle');
    
    // Login page
    const loginTitle = document.querySelector('.form-title');
    if (loginTitle) {
        const titleText = loginTitle.getAttribute('data-translate');
        if (titleText === 'login.title') {
            loginTitle.innerHTML = `🌱 ${t('login.title')}`;
        } else if (titleText) {
            loginTitle.textContent = t(titleText);
        }
    }
    
    // Buy page - preserve emoji
    const buyTitle = document.querySelector('.page-header h1[data-translate="buy.title"]');
    if (buyTitle) {
        buyTitle.innerHTML = `🛒 ${t('buy.title')}`;
    }
    
    // Sell page - preserve emoji
    const sellTitle = document.querySelector('.page-header h1[data-translate="sell.title"]');
    if (sellTitle) {
        sellTitle.innerHTML = `🌾 ${t('sell.title')}`;
    }
    
    // Market page - preserve emojis
    const marketTitle = document.querySelector('.page-header h1[data-translate="market.title"]');
    if (marketTitle) {
        marketTitle.innerHTML = `📊 ${t('market.title')}`;
    }
    
    // Market page H2 headings - preserve emojis
    const latestNewsHeading = document.querySelector('h2[data-translate="market.latestNews"]');
    if (latestNewsHeading) {
        latestNewsHeading.innerHTML = `📈 ${t('market.latestNews')}`;
    }
    
    const marketAnalysisHeading = document.querySelector('h2[data-translate="market.analysis"]');
    if (marketAnalysisHeading) {
        marketAnalysisHeading.innerHTML = `📊 ${t('market.analysis')}`;
    }
    
    // Refresh button - preserve emoji
    const refreshBtn = document.querySelector('.refresh-btn[data-translate="market.refresh"]');
    if (refreshBtn) {
        refreshBtn.innerHTML = `🔄 ${t('market.refresh')}`;
    }
    
    // Chatbot
    const chatbotTitle = document.querySelector('.chatbot-header-text h3');
    if (chatbotTitle) chatbotTitle.textContent = t('chatbot.title');
    
    const chatbotOnline = document.querySelector('.chatbot-header-text p');
    if (chatbotOnline) chatbotOnline.textContent = t('chatbot.online');
    
    const chatbotInput = document.getElementById('chatbot-input');
    if (chatbotInput) chatbotInput.placeholder = t('chatbot.placeholder');
}

// Initialize translation on page load
document.addEventListener('DOMContentLoaded', function() {
    translatePage();
    updateLanguageButton();
});

