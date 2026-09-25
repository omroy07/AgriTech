/**
 * AgriTech Hyperlocal Voice Assistant & Voice Input Module
 * - Multilingual Speech-to-Text & Text-to-Speech (Online Gemini 2.5 Flash + Offline Local Fallback)
 * - Multimodal Camera / Image Disease Diagnosis Integration
 * - Floating PWA Voice Assistant Widget (#agri-voice-assistant)
 * - Offline Fallback Agronomy Knowledge Base & Speech Synthesis
 * - Form Voice-to-Text Enhancement
 */

// -----------------------------------------------------------------------------
// 1. OFFLINE AGRONOMY KNOWLEDGE BASE (Multi-language local fallback)
// -----------------------------------------------------------------------------
const OFFLINE_AGRI_KB = [
  {
    tags: ["tomato", "blight", "black spot", "टमाटर", "झुलसा", "करपा", "తెగులు"],
    title: "Tomato Blight & Leaf Spot Management",
    hi: "टमाटर में झुलसा (Blight) का उपाय:\n• 🌿 जैविक उपचार: 5 मिली नीम का तेल प्रति लीटर पानी में मिलाकर 7 दिन के अंतराल पर छिड़कें।\n• 🧪 रासायनिक: कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) या मैंकोजेब का छिड़काव करें।\n• 🛡️ रोकथाम: संक्रमित पत्तियां तोड़कर नष्ट करें और शाम को पानी देने से बचें।",
    en: "Tomato Blight Management:\n• 🌿 Organic: Spray Neem Oil (5ml/L water) or Trichoderma viride every 7 days.\n• 🧪 Chemical: Spray Copper Oxychloride (2.5g/L) or Mancozeb.\n• 🛡️ Prevention: Remove infected lower foliage and avoid sprinkler wetting of leaves.",
    mr: "टोमॅटो करपा (Blight) नियंत्रण:\n• 🌿 सेंद्रिय: ५ मिली निंबोळी तेल प्रति लिटर पाण्यात मिसळून फवारा.\n• 🧪 रासायनिक: कॉपर ऑक्सिक्लोराईड (२.५ ग्रॅम/लिटर) फवारा.\n• 🛡️ खबरदारी: रोपांच्या पानांवर पाणी साचू देऊ नका.",
    te: "టమోటా ఆకుమచ్చ & తెగులు నివారణ:\n• 🌿 సేంద్రీయ: వేప నూనె (5ml/లీ) 7 రోజుల వ్యవధిలో పిచికారీ చేయండి.\n• 🧪 రసాయన: కాపర్ ఆక్సిక్లోరైడ్ (2.5 గ్రా/లీ) వాడండి.\n• 🛡️ నివారణ: సోకిన ఆకులను తీసివేయండి.",
    ta: "தக்காளி இலைக்கருகல் நோய் மேலாண்மை:\n• 🌿 இயற்கை: வேப்பெண்ணெய் (5மி.லி/லிட்டர்) தெளிக்கவும்.\n• 🧪 ரசாயனம்: காப்பர் ஆக்ஸிகுளோரைடு (2.5 கிராம்/லிட்டர்) தெளிக்கவும்.\n• 🛡️ தடுப்பு: பாதிக்கப்பட்ட இலைகளை அகற்றவும்."
  },
  {
    tags: ["fertilizer", "npk", "urea", "dap", "खाद", "उर्वरक", "खत", "ఎరువు", "உரம்"],
    title: "Balanced Fertilizer & Soil Nutrition",
    hi: "संतुलित उर्वरक प्रबंधन सलाह:\n• 🌾 बेसल डोज: बुवाई के समय DAP या NPK 19:19:19 और 5 टन सड़ी गोबर खाद डालें।\n• 🌱 यूरिया: यूरिया को हमेशा 2-3 खुराकों में सिंचाई के तुरंत बाद दें।\n• 🍂 सूक्ष्म पोषक: फूल और फल आते समय जिंक सल्फेट और बोरॉन का पर्णीय छिड़काव करें।",
    en: "Balanced Fertilizer Advisory:\n• 🌾 Basal Dose: Apply DAP or NPK 19:19:19 at sowing with well-decomposed FYM.\n• 🌱 Urea: Split Urea into 2-3 top dressings after light irrigation.\n• 🍂 Micronutrients: Foliar spray of Zinc Sulfate & Boron during flowering.",
    mr: "संतुलित खत व्यवस्थापन:\n• 🌾 पेरणीवेळी DAP किंवा NPK 19:19:19 आणि शेणखत टाका.\n• 🌱 युरिया २ ते ३ हप्त्यांत विभागून द्या.\n• 🍂 फुलधारणेच्या वेळी सूक्ष्म अन्नद्रव्यांची फवारणी करा.",
    te: "సమతుల్య ఎరువుల యాజమాన్యం:\n• 🌾 విత్తే సమయంలో DAP లేదా NPK 19:19:19 వేయండి.\n• 🌱 యూరియాను విడతల వారీగా తడి ఆరిన తర్వాత మాత్రమే చల్లండి.\n• 🍂 పూత సమయంలో జింక్, బోరాన్ పిచికారీ చేయండి.",
    ta: "சீரான உர மேலாண்மை:\n• 🌾 விதைப்பின் போது DAP அல்லது NPK 19:19:19 மற்றும் தொழு உரம் இடவும்.\n• 🌱 யூரியாவை 2-3 தவணைகளாக பிரித்து இடவும்."
  },
  {
    tags: ["pm kisan", "scheme", "subsidy", "योजना", "पीएम किसान", "ਸਕੀਮ", "పథకం", "திட்டம்"],
    title: "Government Schemes & PM-KISAN",
    hi: "सरकारी कृषि योजनाएं व सहायता:\n• 💰 PM-KISAN: पात्र किसानों को सालाना ₹6,000 (3 किश्तों में) मिलते हैं। e-KYC अवश्य पूरी रखें।\n• 🛡️ PMFBY: प्रधानमंत्री फसल बीमा योजना में प्रतिकूल मौसम से फसल नुकसान पर क्लेम 72 घंटे में दर्ज करें।\n• 📞 किसान कॉल सेंटर टोल-फ्री: 1800-180-1551 पर संपर्क करें।",
    en: "Government Agricultural Schemes:\n• 💰 PM-KISAN: ₹6,000/year direct transfer for registered farmers. Ensure e-KYC is active.\n• 🛡️ PMFBY: Pradhan Mantri Fasal Bima Yojana covers crop loss from drought/flood (Report in 72 hrs).\n• 📞 Kisan Call Center Helpline: 1800-180-1551 (Toll-Free).",
    mr: "शासकीय शेतकरी योजना:\n• 💰 पीएम किसान: वार्षिक ₹६,००० थेट बँक खात्यात. e-KYC पूर्ण ठेवा.\n• 🛡️ पीक विमा: नुकसान झाल्यास ७२ तासांत तक्रार नोंदवा.\n• 📞 किसान कॉल सेंटर: १८००-१८०-१५५१",
    te: "ప్రభుత్వ వ్యవసాయ పథకాలు:\n• 💰 పీఎం కిసాన్: అర్హులైన రైతులకు ఏడాదికి ₹6,000 అందుతాయి.\n• 🛡️ ప్రధానమంత్రి ఫసల్ బీమా యోజన కింద పంట నష్టం నమోదు చేసుకోండి.\n• 📞 కిసాన్ కాల్ సెంటర్: 1800-180-1551",
    ta: "அரசு மானிய திட்டங்கள்:\n• 💰 பி.எம் கிசான்: வருடத்திற்கு ₹6,000 நிதி உதவி.\n• 🛡️ பயிர் காப்பீட்டுத் திட்டம் மூலம் இழப்பீடு பெறலாம்.\n• 📞 உழவர் உதவி எண்: 1800-180-1551"
  },
  {
    tags: ["pest", "insect", "aphid", "caterpillar", "कीट", "मावा", "इल्ली", "పురుగు", "பூச்சி"],
    title: "Organic Pest & Insect Control",
    hi: "जैविक कीट नियंत्रण उपाय:\n• 🍃 नीम अर्क: 5% नीम बीज अर्क या 10,000 PPM नीम तेल का छिड़काव रस चूसक कीटों को रोकता है।\n• 🟡 फेरोमोन व येलो स्टिकी ट्रैप: प्रति एकड़ 5-6 ट्रैप लगाकर कीटों की निगरानी करें।\n• 🧪 गंभीर प्रकोप: अनुशंसित कीटनाशक जैसे इमिडाक्लोप्रिड या क्लोरेंट्रानिलिप्रोल का लेबल अनुसार प्रयोग करें।",
    en: "Organic & Integrated Pest Management:\n• 🍃 Neem Solution: 5ml Neem Oil/L or 5% NSKE controls sucking pests (whiteflies, aphids).\n• 🟡 Traps: Install 5-6 Yellow Sticky & Pheromone traps per acre for early interception.\n• 🧪 Severe Infestation: Use target-specific bio-pesticides or recommended spray.",
    mr: "सेंद्रिय कीड नियंत्रण:\n• 🍃 निंबोळी अर्क: रसशोषक किडींसाठी ५% निंबोळी अर्काची फवारणी करा.\n• 🟡 चिकट सापळे: एकरी ५ पिवळे व निळे चिकट सापळे लावा.\n• 🧪 गरज भासल्यास शिफारशीत कीटकनाशक वापरा.",
    te: "సేంద్రీయ పురుగుల నివారణ:\n• 🍃 వేప నూనె: రసం పీల్చే పురుగుల నివారణకు వేప నూనె వాడండి.\n• 🟡 పసుపు జిగురు బోర్డులు ఎకరానికి 6 ఏర్పాటు చేయండి.",
    ta: "இயற்கை பூச்சி கட்டுப்பாடு:\n• 🍃 வேப்பெண்ணெய் கரைசல் சிறந்த பூச்சி விரட்டியாகும்.\n• 🟡 மஞ்சள் ஒட்டும் பொறிகளை வயலில் அமைக்கவும்."
  },
  {
    tags: ["wheat", "rust", "गेहूं", "రస్ట్", "கோதுமை"],
    title: "Wheat Crop Care & Rust Prevention",
    hi: "गेहूं फसल देखभाल और रतुआ (Rust) नियंत्रण:\n• 🌾 पीला/भूरा रतुआ लक्षण: पत्तियों पर पीले-भूरे रंग के पाउडर जैसे धब्बे।\n• 🧪 उपचार: प्रोपिकोनाजोल 25% EC (1 मिली/लीटर) पानी में घोलकर तुरंत छिड़काव करें।\n• 💧 सिंचाई: पहली सिंचाई बुवाई के 21 दिन बाद (CRI स्टेज) पर अवश्य दें।",
    en: "Wheat Care & Rust Control:\n• 🌾 Rust Symptoms: Yellow or brown powdery pustules on foliage.\n• 🧪 Treatment: Spray Propiconazole 25% EC @ 1ml/L at earliest symptom onset.\n• 💧 Irrigation: Critical first irrigation at Crown Root Initiation (CRI) stage (21 DAS).",
    mr: "गहू पीक व्यवस्थापन:\n• 🌾 तांबेरा रोग: पानांवर पिवळसर-तपकिरी ठिपके.\n• 🧪 उपाय: प्रोपिकोनाझोल १ मिली/लिटर पाण्यात फवारा.\n• 💧 पहिली पाणी पाळी पेरणीनंतर २१ दिवसांनी द्या.",
    te: "గోధుమ పంట సంరక్షణ:\n• 🌾 తుప్పు తెగులు నివారణకు ప్రొపికోనజోల్ 1ml/L పిచिकారీ చేయండి.\n• 💧 21వ రోజున మొదటి తడి తప్పనిసరిగా ఇవ్వండి."
  },
  {
    tags: ["rice", "paddy", "blast", "धान", "चावल", "వరి", "நெல்"],
    title: "Rice / Paddy Blast & Water Management",
    hi: "धान (Paddy) ब्लास्ट रोग व पोषण:\n• 🌾 ब्लास्ट लक्षण: पत्तियों पर आंख के आकार के भूरे धब्बे।\n• 🧪 उपचार: ट्राइसाइक्लाजोल 75% WP (0.6 ग्राम/लीटर) का छिड़काव करें।\n• 💧 जल प्रबंधन: कल्ले फूटते समय और बाली निकलते समय खेत में 2-3 सेमी पानी बनाए रखें।",
    en: "Paddy Blast & Water Management:\n• 🌾 Blast Symptoms: Spindle/eye-shaped lesions with gray centers.\n• 🧪 Treatment: Spray Tricyclazole 75% WP (0.6g/L) or Isoprothiolane.\n• 💧 Water: Maintain 2-3 cm shallow water layer during tillering and panicle emergence.",
    mr: "भात पिकावरील करपा व पाणी व्यवस्थापन:\n• 🌾 करपा रोग: पानांवर डोळ्याच्या आकाराचे ठिपके.\n• 🧪 उपाय: ट्रायसायक्लॅझोल ०.६ ग्रॅम/लिटर फवारा.\n• 💧 फुटवे फुटताना शेतात पाणी साठवून ठेवा.",
    te: "వరి అగ్గితెగులు నివారణ:\n• 🌾 ట్రైసైక్లాజోల్ 75% WP (0.6 గ్రా/లీ) పిచికారీ చేయండి.\n• 💧 పిలకలు వేసే దశలో నీటి నిల్వ ఉంచండి."
  }
];

// -----------------------------------------------------------------------------
// 2. VOICE INPUT MANAGER (Inline Form Inputs)
// -----------------------------------------------------------------------------
class VoiceInputManager {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.currentInput = null;
    this.supportedLanguages = {
      'hi-IN': 'Hindi (हिंदी)',
      'en-IN': 'English (India)',
      'mr-IN': 'Marathi (मराठी)',
      'te-IN': 'Telugu (తెలుగు)',
      'ta-IN': 'Tamil (தமிழ்)',
      'kn-IN': 'Kannada (ಕನ್ನಡ)',
      'pa-IN': 'Punjabi (ਪੰਜਾਬੀ)',
      'gu-IN': 'Gujarati (ગુજરાતી)',
      'bn-IN': 'Bengali (বাংলা)',
      'ml-IN': 'Malayalam (മലയാളം)'
    };
    this.currentLanguage = localStorage.getItem('agritech_voice_lang') || 'hi-IN';
    this.initializeRecognition();
  }

  initializeRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('Web Speech Recognition not supported in this browser');
      return false;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = this.currentLanguage;

    this.recognition.onstart = () => {
      this.isListening = true;
      this.updateButtonState(this.currentInput, 'listening');
      this.showFeedback('Listening... Speak now 🎙️', 'info');
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;

      if (this.currentInput) {
        const currentValue = this.currentInput.value.trim();
        this.currentInput.value = currentValue ? `${currentValue} ${transcript}` : transcript;
        this.currentInput.dispatchEvent(new Event('input', { bubbles: true }));
        this.currentInput.dispatchEvent(new Event('change', { bubbles: true }));
      }
      this.showFeedback(`Captured: "${transcript}" (${Math.round(confidence * 100)}%)`, 'success');
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      this.updateButtonState(this.currentInput, 'error');
      let msg = 'Voice input note: ';
      switch (event.error) {
        case 'no-speech': msg += 'No speech heard. Tap and speak again.'; break;
        case 'not-allowed': msg += 'Microphone access denied. Allow permission in browser.'; break;
        case 'network': msg += 'Network busy. Using offline fallback.'; break;
        default: msg += event.error;
      }
      this.showFeedback(msg, 'error');
    };

    this.recognition.onend = () => {
      this.isListening = false;
      this.updateButtonState(this.currentInput, 'ready');
    };
    return true;
  }

  setLanguage(langCode) {
    if (this.supportedLanguages[langCode]) {
      this.currentLanguage = langCode;
      if (this.recognition) {
        this.recognition.lang = langCode;
      }
      localStorage.setItem('agritech_voice_lang', langCode);
    }
  }

  startListening(inputElement) {
    if (!this.recognition) {
      this.showFeedback('Voice input not supported in your browser', 'error');
      return;
    }
    if (this.isListening) {
      this.stopListening();
      return;
    }
    this.currentInput = inputElement;
    try {
      this.recognition.start();
    } catch (e) {
      console.warn('Recognition start exception:', e);
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      try { this.recognition.stop(); } catch (e) {}
    }
  }

  updateButtonState(inputElement, state) {
    if (!inputElement) return;
    const button = inputElement.parentElement?.querySelector('.voice-btn');
    if (!button) return;
    button.classList.remove('listening', 'error', 'ready');
    button.classList.add(state);
    const icon = button.querySelector('i');
    if (icon) {
      if (state === 'listening') {
        icon.className = 'fas fa-microphone-slash';
        button.title = 'Listening... Click to stop';
      } else if (state === 'error') {
        icon.className = 'fas fa-exclamation-circle';
        button.title = 'Error - Click to retry';
        setTimeout(() => {
          icon.className = 'fas fa-microphone';
          button.title = 'Click to speak';
          button.classList.remove('error');
        }, 3000);
      } else {
        icon.className = 'fas fa-microphone';
        button.title = 'Click to speak';
      }
    }
  }

  showFeedback(message, type = 'info') {
    let feedback = document.getElementById('voice-feedback');
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.id = 'voice-feedback';
      feedback.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        max-width: 320px;
        padding: 12px 18px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.18);
        z-index: 100000;
        font-size: 13.5px;
        font-family: inherit;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.3s ease;
      `;
      document.body.appendChild(feedback);
    }

    const colors = {
      info: { bg: '#e0f2fe', border: '#0284c7', text: '#0369a1' },
      success: { bg: '#ecfdf5', border: '#10b981', text: '#065f46' },
      error: { bg: '#fef2f2', border: '#ef4444', text: '#991b1b' }
    };
    const c = colors[type] || colors.info;
    feedback.style.backgroundColor = c.bg;
    feedback.style.borderLeft = `5px solid ${c.border}`;
    feedback.style.color = c.text;
    feedback.innerHTML = `<strong>${type === 'success' ? '✓' : type === 'error' ? '!' : 'ℹ'}</strong> <span>${message}</span>`;

    clearTimeout(this._feedbackTimer);
    this._feedbackTimer = setTimeout(() => {
      if (feedback && feedback.parentNode) {
        feedback.remove();
      }
    }, 4000);
  }

  addVoiceButton(inputElement) {
    if (!this.recognition || inputElement.parentElement?.querySelector('.voice-btn')) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'voice-input-wrapper';
    wrapper.style.position = 'relative';
    wrapper.style.display = 'inline-block';
    wrapper.style.width = '100%';

    inputElement.parentNode.insertBefore(wrapper, inputElement);
    wrapper.appendChild(inputElement);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'voice-btn ready';
    button.title = 'Click to speak';
    button.innerHTML = '<i class="fas fa-microphone"></i>';
    button.style.cssText = `
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      background: linear-gradient(135deg, #10b981, #059669);
      border: none;
      border-radius: 50%;
      width: 34px;
      height: 34px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 14px;
      box-shadow: 0 2px 8px rgba(16,185,129,0.3);
      transition: all 0.25s ease;
      z-index: 10;
    `;

    button.addEventListener('click', (e) => {
      e.preventDefault();
      this.startListening(inputElement);
    });

    wrapper.appendChild(button);
    const pad = parseInt(window.getComputedStyle(inputElement).paddingRight || '10') + 40;
    inputElement.style.paddingRight = `${pad}px`;
  }

  initializePageVoiceInputs(selector = 'input[type="text"], input[type="search"], textarea') {
    document.querySelectorAll(selector).forEach(input => {
      if (input.hasAttribute('data-no-voice') || input.parentElement?.classList.contains('voice-input-wrapper') || input.closest('#agri-voice-assistant-modal')) {
        return;
      }
      if (input.offsetParent !== null) {
        this.addVoiceButton(input);
      }
    });
  }
}

// -----------------------------------------------------------------------------
// 3. AGRIBOT HYPERLOCAL VOICE ASSISTANT (Floating PWA & Offline Engine)
// -----------------------------------------------------------------------------
class AgriVoiceAssistant {
  constructor() {
    this.isOpen = false;
    this.isRecording = false;
    this.recognition = null;
    this.currentAudio = null;
    this.selectedImageBase64 = null;
    this.selectedCrop = 'Tomato';
    this.currentLang = localStorage.getItem('agritech_bot_lang') || 'hi';
    this.offlineMode = !navigator.onLine;

    window.addEventListener('online', () => this.handleNetworkChange(true));
    window.addEventListener('offline', () => this.handleNetworkChange(false));

    this.initSpeechEngine();
    this.renderAssistantDOM();
    this.loadHistory();
  }

  handleNetworkChange(isOnline) {
    this.offlineMode = !isOnline;
    const badge = document.getElementById('agri-bot-network-badge');
    if (badge) {
      if (isOnline) {
        badge.className = 'network-badge online';
        badge.innerHTML = '<span class="pulse-dot"></span> Online (Gemini 2.5 Flash)';
      } else {
        badge.className = 'network-badge offline';
        badge.innerHTML = '<span class="pulse-dot offline"></span> Offline Mode (Local AI)';
      }
    }
  }

  initSpeechEngine() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('SpeechRecognition not supported in browser');
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = `${this.currentLang}-IN`;

    this.recognition.onstart = () => {
      this.isRecording = true;
      this.setRecordingUI(true);
      const statusText = document.getElementById('agri-voice-status-text');
      if (statusText) statusText.innerText = 'Listening... Speak your crop question 🌾';
    };

    this.recognition.onresult = (event) => {
      const transcript = Array.from(event.results).map(r => r[0].transcript).join('');
      const inputField = document.getElementById('agri-voice-text-input');
      if (inputField) inputField.value = transcript;

      if (event.results[0].isFinal) {
        this.submitQuery(transcript);
      }
    };

    this.recognition.onerror = (event) => {
      console.warn('Voice assistant recognition error:', event.error);
      this.isRecording = false;
      this.setRecordingUI(false);
      const statusText = document.getElementById('agri-voice-status-text');
      if (statusText) statusText.innerText = 'Tap mic to speak or type query below.';
    };

    this.recognition.onend = () => {
      this.isRecording = false;
      this.setRecordingUI(false);
    };
  }

  setRecordingUI(active) {
    const micBtn = document.getElementById('agri-voice-mic-main');
    const waveEl = document.getElementById('agri-voice-wave');
    if (micBtn) {
      if (active) {
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<i class="fas fa-stop"></i>';
      } else {
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
      }
    }
    if (waveEl) {
      waveEl.style.display = active ? 'flex' : 'none';
    }
  }

  toggleRecording() {
    if (!this.recognition) {
      alert('Speech recognition is not available in your browser. Please type your query.');
      return;
    }
    if (this.isRecording) {
      this.recognition.stop();
    } else {
      this.recognition.lang = `${this.currentLang}-IN`;
      try {
        this.recognition.start();
      } catch (e) {
        console.warn('Recognition start retry:', e);
      }
    }
  }

  // Multimodal Image Attachment
  handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      this.selectedImageBase64 = e.target.result;
      const previewCont = document.getElementById('agri-voice-img-preview-cont');
      const previewImg = document.getElementById('agri-voice-img-preview');
      if (previewImg && previewCont) {
        previewImg.src = this.selectedImageBase64;
        previewCont.style.display = 'flex';
      }
    };
    reader.readAsDataURL(file);
  }

  removeAttachedImage() {
    this.selectedImageBase64 = null;
    const previewCont = document.getElementById('agri-voice-img-preview-cont');
    const inputEl = document.getElementById('agri-voice-photo-input');
    if (previewCont) previewCont.style.display = 'none';
    if (inputEl) inputEl.value = '';
  }

  // Match query against offline agronomy knowledge base
  getOfflineAnswer(queryText) {
    const q = (queryText || '').toLowerCase();
    for (const item of OFFLINE_AGRI_KB) {
      if (item.tags.some(t => q.includes(t.toLowerCase()))) {
        const text = item[this.currentLang] || item.hi || item.en;
        return {
          title: item.title,
          text: text,
          offline: true
        };
      }
    }
    // Generic offline fallback
    const defaults = {
      hi: "🌾 ऑफलाइन कृषि मित्र सलाह:\n• मिट्टी में 50-60% नमी बनाए रखें।\n• कीट या फफूंद दिखने पर 5 मिली नीम तेल प्रति लीटर पानी का छिड़काव करें।\n• नेटवर्क मिलने पर पुनः ऑनलाइन सलाह प्राप्त करें। (किसान हेल्पलाइन: 1800-180-1551)",
      en: "🌾 Offline AgriBot Advisory:\n• Maintain 50-60% field moisture capacity.\n• Spray 5ml Neem Oil/L water at early signs of sucking pests or leaf spots.\n• Connect to internet for live Gemini diagnosis. (Kisan Helpline: 1800-180-1551)",
      mr: "🌾 ऑफलाइन शेतकरी सल्ला:\n• जमिनीत योग्य ओलावा राखा.\n• कीड प्रतिबंधासाठी ५ मिली निंबोळी तेल प्रति लिटर फवारा.\n• शेतकरी हेल्पलाइन: १८००-१८०-१५५१",
      te: "🌾 ఆఫ్‌లైన్ రైతు సలహా:\n• నేలలో తగినంత తేమ ఉండేలా చూడండి.\n• పురుగుల నివారణకు వేప నూనె (5ml/L) పిచికారీ చేయండి."
    };
    return {
      title: "Offline Agronomy Guidance",
      text: defaults[this.currentLang] || defaults.en,
      offline: true
    };
  }

  // Local Offline Speech Synthesis (TTS)
  speakOffline(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    // Clean markdown/symbols
    const clean = text.replace(/[\*\_#•\n]+/g, ' ').replace(/[🌿🧪🍃🛡️🌾💰📝🔍🍂🌱]/g, '').slice(0, 300);
    const utterance = new SpeechSynthesisUtterance(clean);

    // Map language code
    const langMap = {
      hi: 'hi-IN', en: 'en-IN', mr: 'mr-IN', te: 'te-IN',
      ta: 'ta-IN', kn: 'kn-IN', pa: 'pa-IN', gu: 'gu-IN', bn: 'bn-IN', ml: 'ml-IN'
    };
    utterance.lang = langMap[this.currentLang] || 'hi-IN';
    utterance.rate = 0.95;

    const btn = document.getElementById('agri-voice-play-tts-btn');
    if (btn) btn.innerHTML = '<i class="fas fa-volume-up"></i> Speaking...';

    utterance.onend = () => {
      if (btn) btn.innerHTML = '<i class="fas fa-play"></i> Replay Voice Note';
    };
    utterance.onerror = () => {
      if (btn) btn.innerHTML = '<i class="fas fa-play"></i> Replay Voice Note';
    };

    window.speechSynthesis.speak(utterance);
  }

  // Play server synthesized MP3 or fallback to SpeechSynthesis
  playAudioResponse(audioInfo, fallbackText) {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }

    const playBtn = document.getElementById('agri-voice-play-tts-btn');

    if (audioInfo && audioInfo.audio_url) {
      this.currentAudio = new Audio(audioInfo.audio_url);
      if (playBtn) playBtn.innerHTML = '<i class="fas fa-volume-up"></i> Playing Audio...';

      this.currentAudio.play().catch(() => {
        // Autoplay policy fallback -> use SpeechSynthesis
        this.speakOffline(fallbackText);
      });

      this.currentAudio.onended = () => {
        if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i> Replay Voice Note';
      };
    } else if (audioInfo && audioInfo.audio_base64) {
      this.currentAudio = new Audio(`data:audio/mp3;base64,${audioInfo.audio_base64}`);
      if (playBtn) playBtn.innerHTML = '<i class="fas fa-volume-up"></i> Playing Audio...';
      this.currentAudio.play().catch(() => this.speakOffline(fallbackText));
      this.currentAudio.onended = () => {
        if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i> Replay Voice Note';
      };
    } else {
      this.speakOffline(fallbackText);
    }
  }

  // Submit query to Backend or Offline Engine
  async submitQuery(customText) {
    const textInput = document.getElementById('agri-voice-text-input');
    const query = (customText || textInput?.value || '').trim();
    const hasImage = !!this.selectedImageBase64;

    if (!query && !hasImage) {
      alert('Please speak or type a question, or attach a plant leaf photo.');
      return;
    }

    const statusText = document.getElementById('agri-voice-status-text');
    const resultsCont = document.getElementById('agri-voice-results');
    const cropSelect = document.getElementById('agri-voice-crop-select');

    if (cropSelect) this.selectedCrop = cropSelect.value;
    if (statusText) statusText.innerText = 'Analyzing with AgriBot AI... 🌾';

    // Show loading skeleton
    resultsCont.style.display = 'block';
    resultsCont.innerHTML = `
      <div class="bot-loading-card">
        <div class="bot-spinner"></div>
        <p>Consulting Agricultural Intelligence & Gemini 2.5 Flash...</p>
      </div>
    `;

    // 1. OFFLINE PATH
    if (!navigator.onLine) {
      setTimeout(() => {
        const offlineRes = this.getOfflineAnswer(query);
        this.renderResponseUI({
          query: query,
          reply_text: offlineRes.text,
          language: this.currentLang,
          isOffline: true
        });
        this.saveHistory({
          query: query,
          reply_text: offlineRes.text,
          date: new Date().toLocaleTimeString(),
          isOffline: true
        });
        this.speakOffline(offlineRes.text);
      }, 500);
      return;
    }

    // 2. ONLINE BACKEND PATH (/api/v1/bot/query)
    try {
      const payload = {
        query: query,
        crop_type: this.selectedCrop,
        language: this.currentLang,
        image_base64: this.selectedImageBase64,
        generate_audio: true
      };

      const response = await fetch('/api/v1/bot/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error(`HTTP Error ${response.status}`);

      const data = await response.json();
      this.renderResponseUI(data);
      this.saveHistory({
        query: query || 'Crop Photo Diagnosis',
        reply_text: data.reply_text,
        diagnosis: data.diagnosis,
        audio_url: data.audio?.audio_url,
        date: new Date().toLocaleTimeString(),
        isOffline: false
      });

      // Play Voice Note
      this.playAudioResponse(data.audio, data.reply_text);

    } catch (err) {
      console.warn('Online bot request failed, switching to offline fallback:', err);
      const offlineRes = this.getOfflineAnswer(query);
      this.renderResponseUI({
        query: query,
        reply_text: offlineRes.text,
        language: this.currentLang,
        isOffline: true,
        networkFallback: true
      });
      this.speakOffline(offlineRes.text);
    }
  }

  renderResponseUI(data) {
    const resultsCont = document.getElementById('agri-voice-results');
    const statusText = document.getElementById('agri-voice-status-text');
    if (statusText) statusText.innerText = 'Advisory ready! Listen or read below 🎧';

    let diagnosisHTML = '';
    if (data.diagnosis && data.diagnosis.success) {
      const diag = data.diagnosis.diagnosis || {};
      const severityColor = diag.severity === 'HIGH' ? '#ef4444' : diag.severity === 'MEDIUM' ? '#f59e0b' : '#10b981';
      diagnosisHTML = `
        <div class="diagnosis-card">
          <div class="diag-header">
            <span class="diag-badge" style="background: ${severityColor}">🌿 ${diag.disease_name || 'Plant Condition'}</span>
            <span class="diag-sev">Severity: <strong>${diag.severity || 'LOW'}</strong></span>
          </div>
          ${diag.symptoms ? `<p class="diag-symptom"><strong>Symptoms:</strong> ${diag.symptoms}</p>` : ''}
        </div>
      `;
    }

    const formattedText = (data.reply_text || '')
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    resultsCont.innerHTML = `
      <div class="bot-response-card ${data.isOffline ? 'offline-card' : ''}">
        ${data.isOffline ? `<div class="offline-tag"><i class="fas fa-wifi-slash"></i> Offline Mode Response</div>` : ''}
        ${diagnosisHTML}
        <div class="bot-text-body">${formattedText}</div>
        <div class="bot-audio-toolbar">
          <button id="agri-voice-play-tts-btn" class="bot-btn-play">
            <i class="fas fa-play"></i> Replay Voice Note
          </button>
          <button id="agri-voice-clear-btn" class="bot-btn-secondary">
            <i class="fas fa-trash-alt"></i> Clear
          </button>
        </div>
      </div>
    `;

    document.getElementById('agri-voice-play-tts-btn')?.addEventListener('click', () => {
      this.playAudioResponse(data.audio, data.reply_text);
    });

    document.getElementById('agri-voice-clear-btn')?.addEventListener('click', () => {
      resultsCont.style.display = 'none';
      resultsCont.innerHTML = '';
      this.removeAttachedImage();
      const textInput = document.getElementById('agri-voice-text-input');
      if (textInput) textInput.value = '';
      if (statusText) statusText.innerText = 'Tap mic to ask agricultural advice.';
    });
  }

  saveHistory(item) {
    try {
      const hist = JSON.parse(localStorage.getItem('agritech_bot_history') || '[]');
      hist.unshift(item);
      if (hist.length > 10) hist.pop();
      localStorage.setItem('agritech_bot_history', JSON.stringify(hist));
      this.loadHistory();
    } catch (e) {}
  }

  loadHistory() {
    const listEl = document.getElementById('agri-voice-history-list');
    if (!listEl) return;
    try {
      const hist = JSON.parse(localStorage.getItem('agritech_bot_history') || '[]');
      if (hist.length === 0) {
        listEl.innerHTML = '<p class="empty-hist">No recent queries. Speak into mic to start!</p>';
        return;
      }
      listEl.innerHTML = hist.map(h => `
        <div class="hist-item">
          <div class="hist-top">
            <span class="hist-query">💬 ${h.query}</span>
            <span class="hist-time">${h.date}</span>
          </div>
        </div>
      `).join('');
    } catch (e) {}
  }

  toggleAssistantModal() {
    this.isOpen = !this.isOpen;
    const modal = document.getElementById('agri-voice-assistant-modal');
    const floatBtn = document.getElementById('agri-voice-floating-btn');
    if (modal) {
      if (this.isOpen) {
        modal.classList.add('active');
        floatBtn.classList.add('active');
      } else {
        modal.classList.remove('active');
        floatBtn.classList.remove('active');
        if (this.isRecording && this.recognition) this.recognition.stop();
        if (this.currentAudio) this.currentAudio.pause();
        window.speechSynthesis?.cancel();
      }
    }
  }

  // RENDER DOM & CSS
  renderAssistantDOM() {
    if (document.getElementById('agri-voice-assistant-container')) return;

    const container = document.createElement('div');
    container.id = 'agri-voice-assistant-container';
    container.innerHTML = `
      <!-- Floating Trigger Button -->
      <button id="agri-voice-floating-btn" class="agri-floating-mic-btn" title="AgriBot Voice Assistant & Crop Advisory">
        <div class="mic-icon-wrapper">
          <i class="fas fa-microphone"></i>
        </div>
        <span class="mic-floating-label">Voice Advisory</span>
        <span class="pulse-ring"></span>
      </button>

      <!-- Floating Assistant Drawer / Modal -->
      <div id="agri-voice-assistant-modal" class="agri-voice-modal">
        <div class="modal-header">
          <div class="header-branding">
            <div class="bot-avatar"><i class="fas fa-seedling"></i></div>
            <div>
              <h3>🌾 AgriBot Voice Assistant</h3>
              <div id="agri-bot-network-badge" class="network-badge ${navigator.onLine ? 'online' : 'offline'}">
                <span class="pulse-dot ${navigator.onLine ? '' : 'offline'}"></span>
                ${navigator.onLine ? 'Online (Gemini 2.5 Flash)' : 'Offline Mode (Local AI)'}
              </div>
            </div>
          </div>
          <button id="agri-voice-close-btn" class="modal-close-btn" title="Close Assistant">&times;</button>
        </div>

        <div class="modal-body">
          <!-- Language & Crop Filter Bar -->
          <div class="agri-filter-bar">
            <div class="filter-group">
              <label><i class="fas fa-language"></i> Language:</label>
              <select id="agri-voice-lang-select">
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="mr">मराठी (Marathi)</option>
                <option value="te">తెలుగు (Telugu)</option>
                <option value="ta">தமிழ் (Tamil)</option>
                <option value="kn">ಕನ್ನಡ (Kannada)</option>
                <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
                <option value="gu">ગુજરાતી (Gujarati)</option>
                <option value="bn">বাংলা (Bengali)</option>
                <option value="ml">മലയാളം (Malayalam)</option>
                <option value="en">English (Indian Agri)</option>
              </select>
            </div>
            <div class="filter-group">
              <label><i class="fas fa-leaf"></i> Crop:</label>
              <select id="agri-voice-crop-select">
                <option value="Tomato">Tomato (टमाटर)</option>
                <option value="Wheat">Wheat (गेहूं)</option>
                <option value="Rice">Rice/Paddy (धान)</option>
                <option value="Cotton">Cotton (कपास)</option>
                <option value="Maize">Maize (मक्का)</option>
                <option value="Sugarcane">Sugarcane (गन्ना)</option>
                <option value="Potato">Potato (आलू)</option>
                <option value="Soybean">Soybean (सोयाबीन)</option>
                <option value="Onion">Onion (प्याज)</option>
              </select>
            </div>
          </div>

          <!-- Main Interactive Voice Core -->
          <div class="voice-hero-card">
            <div id="agri-voice-wave" class="audio-waveform" style="display: none;">
              <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
            </div>

            <button id="agri-voice-mic-main" class="main-mic-trigger" title="Tap to Speak">
              <i class="fas fa-microphone"></i>
            </button>
            <p id="agri-voice-status-text" class="voice-status">Tap microphone to speak your question</p>

            <!-- Multimodal Plant Photo Attachment Preview -->
            <div id="agri-voice-img-preview-cont" class="image-preview-badge" style="display: none;">
              <img id="agri-voice-img-preview" src="" alt="Crop Leaf Attached">
              <span>Leaf Photo Attached for Disease AI</span>
              <button id="agri-voice-remove-img" class="remove-img-btn">&times;</button>
            </div>
          </div>

          <!-- Text Input & Attachment Bar -->
          <div class="agri-input-dock">
            <input type="file" id="agri-voice-photo-input" accept="image/*" capture="environment" style="display: none;">
            <button id="agri-voice-cam-btn" class="dock-btn photo-btn" title="Snap / Upload Leaf Photo">
              <i class="fas fa-camera"></i>
            </button>
            <input type="text" id="agri-voice-text-input" placeholder="Type or speak crop question..." autocomplete="off">
            <button id="agri-voice-send-btn" class="dock-btn send-btn" title="Submit Question">
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>

          <!-- Advisory Output Card -->
          <div id="agri-voice-results" class="results-container" style="display: none;"></div>

          <!-- Recent Advisory History -->
          <div class="agri-history-drawer">
            <h4><i class="fas fa-history"></i> Recent Consultations</h4>
            <div id="agri-voice-history-list" class="history-list"></div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(container);
    this.injectStyles();
    this.attachEventListeners();
  }

  attachEventListeners() {
    document.getElementById('agri-voice-floating-btn')?.addEventListener('click', () => this.toggleAssistantModal());
    document.getElementById('agri-voice-close-btn')?.addEventListener('click', () => this.toggleAssistantModal());
    document.getElementById('agri-voice-mic-main')?.addEventListener('click', () => this.toggleRecording());

    document.getElementById('agri-voice-cam-btn')?.addEventListener('click', () => {
      document.getElementById('agri-voice-photo-input')?.click();
    });

    document.getElementById('agri-voice-photo-input')?.addEventListener('change', (e) => this.handleImageUpload(e));
    document.getElementById('agri-voice-remove-img')?.addEventListener('click', () => this.removeAttachedImage());

    document.getElementById('agri-voice-send-btn')?.addEventListener('click', () => this.submitQuery());
    document.getElementById('agri-voice-text-input')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.submitQuery();
      }
    });

    const langSelect = document.getElementById('agri-voice-lang-select');
    if (langSelect) {
      langSelect.value = this.currentLang;
      langSelect.addEventListener('change', (e) => {
        this.currentLang = e.target.value;
        localStorage.setItem('agritech_bot_lang', this.currentLang);
        if (this.recognition) this.recognition.lang = `${this.currentLang}-IN`;
      });
    }
  }

  injectStyles() {
    const style = document.createElement('style');
    style.id = 'agri-voice-assistant-styles';
    style.textContent = `
      /* FLOATING TRIGGER BUTTON */
      #agri-voice-assistant-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        z-index: 99999;
      }
      .agri-floating-mic-btn {
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        border: none;
        border-radius: 50px;
        padding: 10px 18px 10px 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.45);
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        z-index: 99999;
      }
      .agri-floating-mic-btn:hover {
        transform: translateY(-4px) scale(1.04);
        box-shadow: 0 12px 30px rgba(16, 185, 129, 0.6);
      }
      .mic-icon-wrapper {
        width: 38px;
        height: 38px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 17px;
      }
      .mic-floating-label {
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.3px;
      }
      .pulse-ring {
        position: absolute;
        inset: -4px;
        border-radius: 50px;
        border: 2px solid rgba(16, 185, 129, 0.7);
        animation: pulseWave 2s infinite;
        pointer-events: none;
      }
      @keyframes pulseWave {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.08); opacity: 0; }
        100% { transform: scale(0.95); opacity: 0; }
      }

      /* FLOATING ASSISTANT MODAL */
      .agri-voice-modal {
        position: fixed;
        bottom: 90px;
        right: 24px;
        width: 390px;
        max-width: calc(100vw - 32px);
        max-height: 82vh;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.22);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        z-index: 99999;
        transform: scale(0.85) translateY(20px);
        opacity: 0;
        pointer-events: none;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        border: 1px solid rgba(16, 185, 129, 0.2);
      }
      .agri-voice-modal.active {
        transform: scale(1) translateY(0);
        opacity: 1;
        pointer-events: auto;
      }
      .modal-header {
        background: linear-gradient(135deg, #065f46, #047857);
        color: #ffffff;
        padding: 16px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .header-branding {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .bot-avatar {
        width: 38px;
        height: 38px;
        background: #10b981;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
      }
      .header-branding h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 700;
      }
      .network-badge {
        font-size: 11px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        margin-top: 3px;
        padding: 2px 8px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.2);
      }
      .pulse-dot {
        width: 7px;
        height: 7px;
        background: #34d399;
        border-radius: 50%;
      }
      .pulse-dot.offline { background: #f87171; }
      .modal-close-btn {
        background: transparent;
        border: none;
        color: #ffffff;
        font-size: 24px;
        cursor: pointer;
        line-height: 1;
        padding: 4px;
      }

      .modal-body {
        padding: 16px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 14px;
        background: #f8fafc;
      }

      /* FILTER BAR */
      .agri-filter-bar {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        background: #ffffff;
        padding: 8px 12px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
      }
      .filter-group {
        display: flex;
        flex-direction: column;
        gap: 3px;
      }
      .filter-group label {
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
      }
      .filter-group select {
        font-size: 12px;
        padding: 4px 6px;
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        background: #f8fafc;
        color: #1e293b;
        outline: none;
      }

      /* HERO VOICE MIC */
      .voice-hero-card {
        background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);
        border: 1px dashed #86efac;
        border-radius: 16px;
        padding: 18px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 10px;
        position: relative;
      }
      .main-mic-trigger {
        width: 66px;
        height: 66px;
        border-radius: 50%;
        background: linear-gradient(135deg, #10b981, #059669);
        color: #ffffff;
        border: none;
        font-size: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
        transition: all 0.25s ease;
      }
      .main-mic-trigger:hover {
        transform: scale(1.08);
      }
      .main-mic-trigger.recording {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        animation: pulseRecording 1.2s infinite;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5);
      }
      @keyframes pulseRecording {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.12); }
      }
      .voice-status {
        font-size: 13px;
        color: #475569;
        font-weight: 500;
        margin: 0;
      }

      /* AUDIO WAVEFORM */
      .audio-waveform {
        display: flex;
        gap: 4px;
        align-items: center;
        height: 20px;
      }
      .audio-waveform span {
        width: 3px;
        height: 100%;
        background: #10b981;
        border-radius: 3px;
        animation: wavePulse 1s ease-in-out infinite;
      }
      .audio-waveform span:nth-child(2) { animation-delay: 0.15s; }
      .audio-waveform span:nth-child(3) { animation-delay: 0.3s; }
      .audio-waveform span:nth-child(4) { animation-delay: 0.45s; }
      .audio-waveform span:nth-child(5) { animation-delay: 0.6s; }
      @keyframes wavePulse {
        0%, 100% { transform: scaleY(0.3); }
        50% { transform: scaleY(1.2); }
      }

      /* IMAGE PREVIEW */
      .image-preview-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #ffffff;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid #cbd5e1;
        font-size: 11.5px;
        color: #334155;
      }
      .image-preview-badge img {
        width: 24px;
        height: 24px;
        border-radius: 4px;
        object-fit: cover;
      }
      .remove-img-btn {
        background: none;
        border: none;
        color: #ef4444;
        font-size: 16px;
        cursor: pointer;
      }

      /* INPUT DOCK */
      .agri-input-dock {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 4px 6px;
      }
      .agri-input-dock input[type="text"] {
        flex: 1;
        border: none;
        outline: none;
        font-size: 13.5px;
        padding: 6px 8px;
        background: transparent;
        color: #0f172a;
      }
      .dock-btn {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
      }
      .dock-btn.photo-btn {
        background: #f1f5f9;
        color: #475569;
      }
      .dock-btn.photo-btn:hover { background: #e2e8f0; }
      .dock-btn.send-btn {
        background: #10b981;
        color: #ffffff;
      }
      .dock-btn.send-btn:hover { background: #059669; }

      /* RESPONSE CARD */
      .bot-response-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #10b981;
      }
      .bot-response-card.offline-card {
        border-left-color: #f59e0b;
      }
      .offline-tag {
        font-size: 11px;
        font-weight: 600;
        color: #d97706;
        margin-bottom: 8px;
      }
      .diagnosis-card {
        background: #f0fdf4;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 10px;
        border: 1px solid #bbf7d0;
      }
      .diag-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
      }
      .diag-badge {
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
      }
      .diag-symptom {
        font-size: 12px;
        color: #334155;
        margin: 4px 0 0 0;
      }
      .bot-text-body {
        font-size: 13.5px;
        line-height: 1.55;
        color: #1e293b;
      }
      .bot-audio-toolbar {
        display: flex;
        gap: 8px;
        margin-top: 12px;
      }
      .bot-btn-play {
        background: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .bot-btn-secondary {
        background: #f1f5f9;
        color: #64748b;
        border: none;
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 12px;
        cursor: pointer;
      }
      .bot-loading-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 13px;
        color: #64748b;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
      }
      .bot-spinner {
        width: 24px;
        height: 24px;
        border: 3px solid #e2e8f0;
        border-top-color: #10b981;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }
      @keyframes spin { to { transform: rotate(360deg); } }

      /* HISTORY */
      .agri-history-drawer {
        margin-top: 4px;
      }
      .agri-history-drawer h4 {
        font-size: 12px;
        color: #64748b;
        margin: 0 0 6px 0;
        font-weight: 600;
      }
      .history-list {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .hist-item {
        background: #ffffff;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 12px;
      }
      .hist-top {
        display: flex;
        justify-content: space-between;
        color: #334155;
      }
      .hist-time { color: #94a3b8; font-size: 11px; }
      .empty-hist { font-size: 11.5px; color: #94a3b8; margin: 0; }

      /* DARK THEME COMPATIBILITY */
      [data-theme="dark"] .agri-voice-modal,
      body.dark-theme .agri-voice-modal {
        background: #0f172a;
        border-color: #334155;
        color: #f1f5f9;
      }
      [data-theme="dark"] .modal-body,
      body.dark-theme .modal-body {
        background: #1e293b;
      }
      [data-theme="dark"] .voice-hero-card,
      body.dark-theme .voice-hero-card {
        background: #0f172a;
        border-color: #059669;
      }
      [data-theme="dark"] .voice-status,
      body.dark-theme .voice-status {
        color: #cbd5e1;
      }
      [data-theme="dark"] .agri-filter-bar,
      [data-theme="dark"] .agri-input-dock,
      [data-theme="dark"] .bot-response-card,
      [data-theme="dark"] .hist-item,
      body.dark-theme .agri-filter-bar,
      body.dark-theme .agri-input-dock,
      body.dark-theme .bot-response-card,
      body.dark-theme .hist-item {
        background: #0f172a;
        color: #f1f5f9;
        border-color: #334155;
      }
      [data-theme="dark"] .agri-input-dock input[type="text"],
      body.dark-theme .agri-input-dock input[type="text"] {
        color: #f8fafc;
      }
      [data-theme="dark"] .bot-text-body,
      body.dark-theme .bot-text-body {
        color: #e2e8f0;
      }
    `;
    document.head.appendChild(style);
  }
}

// -----------------------------------------------------------------------------
// 4. AUTO-INITIALIZATION
// -----------------------------------------------------------------------------
const voiceInputManager = new VoiceInputManager();
let agriVoiceAssistant = null;

function initAgriVoiceSystem() {
  voiceInputManager.initializePageVoiceInputs();
  if (!agriVoiceAssistant) {
    agriVoiceAssistant = new AgriVoiceAssistant();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAgriVoiceSystem);
} else {
  initAgriVoiceSystem();
}

// Expose globally
window.voiceInputManager = voiceInputManager;
window.agriVoiceAssistant = agriVoiceAssistant;
