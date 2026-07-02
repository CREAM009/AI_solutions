document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.querySelector('.navbar');
  const fadeElements = document.querySelectorAll('.fade-up');
  const counters = document.querySelectorAll('.counter');
  const chatToggle = document.querySelector('.chatbot-toggle');
  const chatCard = document.getElementById('chatbotCard');
  const chatClose = document.querySelector('.chatbot-close');
  const chatInput = document.getElementById('chatInput');
  const contactForm = document.getElementById('contactForm');
  const formMessage = document.getElementById('formMessage');

  const handleScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  };

  const revealOnScroll = () => {
    fadeElements.forEach((element) => {
      const rect = element.getBoundingClientRect();
      if (rect.top < window.innerHeight - 80) {
        element.classList.add('visible');
      }
    });
  };

  const animateCounters = () => {
    counters.forEach((counter) => {
      if (counter.dataset.animated) return;
      const target = Number(counter.dataset.target);
      const suffix = counter.textContent.includes('+') ? '+' : '';
      const duration = 1400;
      const startTime = performance.now();

      const tick = (currentTime) => {
        const progress = Math.min((currentTime - startTime) / duration, 1);
        const value = Math.floor(progress * target);
        counter.textContent = `${value}${suffix}`;
        if (progress < 1) requestAnimationFrame(tick);
        else counter.dataset.animated = 'true';
      };

      requestAnimationFrame(tick);
    });
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCounters();
        observer.disconnect();
      }
    });
  }, { threshold: 0.5 });

  const statsSection = document.querySelector('.stats-section');
  if (statsSection) observer.observe(statsSection);

  window.addEventListener('scroll', () => {
    handleScroll();
    revealOnScroll();
  });

  handleScroll();
  revealOnScroll();

  chatToggle?.addEventListener('click', () => {
    chatCard?.classList.toggle('open');
  });

  chatClose?.addEventListener('click', () => {
    chatCard?.classList.remove('open');
  });

  const scrollChatToBottom = () => {
    const body = document.querySelector('.chatbot-body');
    if (body) {
      body.scrollTop = body.scrollHeight;
    }
  };

  const addMessage = (text, type = 'assistant') => {
    const body = document.querySelector('.chatbot-body');
    if (!body) return;

    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.textContent = text;
    body.appendChild(div);
    scrollChatToBottom();
  };

  const showTypingIndicator = () => {
    const body = document.querySelector('.chatbot-body');
    if (!body) return null;

    const typing = document.createElement('div');
    typing.className = 'message assistant typing';
    typing.textContent = 'AI Assistant is typing...';
    body.appendChild(typing);
    scrollChatToBottom();
    return typing;
  };

  const getReply = (input) => {
    const normalized = input.trim().toLowerCase();

    const greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'];
    const companyInfo = ['about', 'company', 'ai solutions', 'who are you'];
    const services = ['services', 'service', 'what do you do', 'solutions', 'what services do you provide'];
    const pricing = ['price', 'pricing', 'cost', 'quote', 'budget', 'how much'];
    const contact = ['contact', 'phone', 'email', 'location', 'address', 'reach us', 'where are you located'];
    const admin = ['admin', 'dashboard', 'login', 'staff'];
    const articles = ['articles', 'blog', 'news'];
    const events = ['events', 'workshop', 'seminar'];
    const gallery = ['gallery', 'photos', 'images'];
    const feedback = ['feedback', 'reviews', 'rating', 'testimonial', 'testimonials'];
    const assistantTerms = ['chatbot', 'assistant', 'help', 'virtual assistant', 'virtual assistants'];
    const thanks = ['thanks', 'thank you', 'thankyou'];
    const goodbye = ['bye', 'goodbye', 'see you', 'see ya', 'take care'];

    if (greetings.some((term) => normalized.includes(term))) {
      return 'Hello! Welcome to AI-Solutions. How can I assist you today?';
    }

    if (companyInfo.some((term) => normalized.includes(term))) {
      return 'AI-Solutions provides AI-powered software solutions including automation, virtual assistants, analytics, cloud solutions, IT consulting, and custom software development.';
    }

    if (services.some((term) => normalized.includes(term))) {
      return 'We offer Virtual Assistants, Business Automation, Custom Software Development, Data Analytics, Cloud Solutions, and IT Consulting.';
    }

    if (pricing.some((term) => normalized.includes(term))) {
      return 'Our pricing depends on your project requirements, complexity, and delivery timeline. Please submit a Contact Us form for a custom quotation.';
    }

    if (contact.some((term) => normalized.includes(term))) {
      return 'You can contact us using the Contact Us page by filling out the inquiry form. Our team will respond as soon as possible.';
    }

    if (admin.some((term) => normalized.includes(term))) {
      return 'The Admin Dashboard is a secure area where authorized staff manage customer inquiries and website content.';
    }

    if (articles.some((term) => normalized.includes(term))) {
      return 'Our Articles section contains the latest technology news and AI insights.';
    }

    if (events.some((term) => normalized.includes(term))) {
      return 'Our Events page lists our upcoming workshops, seminars, and technology events.';
    }

    if (gallery.some((term) => normalized.includes(term))) {
      return 'Our Gallery showcases company projects, events, and achievements.';
    }

    if (feedback.some((term) => normalized.includes(term))) {
      return 'Our Customer Feedback section contains reviews and ratings from previous clients.';
    }

    if (assistantTerms.some((term) => normalized.includes(term))) {
      return "I'm your virtual assistant. I can answer questions about our company, services, pricing, events, articles, and contact information.";
    }

    if (thanks.some((term) => normalized.includes(term))) {
      return "You're welcome! Let me know if there's anything else I can help you with.";
    }

    if (goodbye.some((term) => normalized.includes(term))) {
      return 'Thank you for visiting AI-Solutions. Have a wonderful day!';
    }

    return "I'm sorry, I couldn't understand your question. I can help with:\n• Services\n• Pricing\n• Contact Information\n• Articles\n• Events\n• Customer Feedback\n• Gallery\n• Admin Dashboard\n\nOr you can submit your inquiry through the Contact Us form.";
  };

  const sendMessage = () => {
    if (!chatInput) return;

    const userText = chatInput.value.trim();
    if (!userText) return;

    addMessage(userText, 'user');
    chatInput.value = '';

    const typingIndicator = showTypingIndicator();
    window.setTimeout(() => {
      if (typingIndicator?.parentNode) {
        typingIndicator.parentNode.removeChild(typingIndicator);
      }
      addMessage(getReply(userText));
    }, 700);
  };

  chatInput?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendMessage();
    }
  });

  contactForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(contactForm);
    formMessage.textContent = 'Sending your inquiry...';

    try {
      const response = await fetch('/contact', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      formMessage.textContent = result.message || 'Thank you for reaching out.';
      if (response.ok) contactForm.reset();
    } catch (error) {
      formMessage.textContent = 'We could not send your message right now. Please try again later.';
    }
  });
});
