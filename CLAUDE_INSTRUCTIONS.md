# Claude Instructions for Bank Communication System Development

# Claude Instructions for Bank Communication System Development

## 🚀 GETTING STARTED - READ THIS FIRST

**GitHub Repository:** https://github.com/longytravel/bank-communication-system

### Initial Setup for New Claude Sessions
1. **Review the GitHub repo** to understand current system state
2. **Check PROJECT_STATUS.md** for latest progress and next priorities  
3. **Review recent commits** to see what was last worked on
4. **Understand the file structure** and existing modules before suggesting changes

### Key Files to Review
- `PROJECT_STATUS.md` - Current progress and next steps
- `src/main.py` - Main application with Cost Management integration
- `src/communication_processing/` - Recently added cost management system
- `requirements.txt` - All dependencies and packages needed
- Recent commits - See what was last implemented

**Always start by saying:** 
> "I've reviewed your GitHub repo and PROJECT_STATUS.md. I can see you're at 85% completion with the cost management system just added. Ready to continue with [next priority]?"

## 🎯 DEVELOPMENT APPROACH - CRITICAL

**These are the user's mandatory working preferences. Follow these exactly:**

### 📋 Step-by-Step Process
- **ONE STEP AT A TIME** - Always break work into individual steps
- **Wait for confirmation** before proceeding to next step
- **Ask "Ready for step X?" or "Please complete this step and let me know when done"**
- **Never assume the user completed a step** - always get confirmation

### 🛠️ Technical Approach  
- **Claude does ALL heavy lifting** - provide complete code, don't ask user to write anything
- **Complete solutions** - never give partial code or "add this somewhere"
- **User is a beginner** - explain what each step does and why
- **No assumptions** - if something could be unclear, explain it
- **Error handling** - always include error handling in code

### 💻 Development Environment
- **Use VS Code, not Notepad:** `code filename.py` instead of `notepad filename.py`
- **VS Code terminal preferred** for all commands
- **Git workflow:** Always stage, commit, and push after major changes
- **File operations:** Use VS Code's integrated terminal and file explorer

### 📁 Project Structure Awareness
```
bank-communication-system/
├── src/
│   ├── api/                    # Claude + OpenAI integrations
│   ├── business_rules/         # Modular rules engine  
│   ├── communication_processing/ # Cost management (NEW)
│   ├── main.py                 # Main Streamlit app
│   └── config.py               # Configuration system
├── data/                       # Data storage
├── PROJECT_STATUS.md           # Current progress tracker
└── requirements.txt            # Dependencies
```

## 🔧 TECHNICAL PREFERENCES

### Code Quality
- **Modular architecture** - separate concerns into different files
- **Comprehensive error handling** - try/except blocks with user-friendly messages
- **Logging integration** - use the existing logging system
- **Type hints** where helpful for clarity
- **Docstrings** for all classes and complex functions

### Integration Patterns
- **Build on existing modules** - leverage api/, business_rules/, config
- **Session state management** - use st.session_state for data persistence
- **Modern UI components** - follow the established styling patterns
- **Cost integration** - always consider cost implications for new features

### Testing Approach
- **Test incrementally** - test each step before moving to next
- **Real data testing** - use sample data when possible
- **Error scenario testing** - test what happens when things go wrong
- **User feedback** - clear success/error messages

## 📊 CURRENT SYSTEM STATUS

### ✅ Completed Systems
- **Customer Analysis:** Claude-powered segmentation with modern UI
- **Cost Management:** Complete system with configurable assumptions and real-time analysis
- **Business Rules:** Modular rules engine with customer category and communication type rules
- **API Integration:** Claude + OpenAI with intelligent rate limiting
- **Main Application:** Professional banking UI with navigation

### 🎯 Next Priority
**Communication Processing Engine** - complete workflow from letter upload to multi-channel communication generation

## 💬 COMMUNICATION STYLE

### User Interaction
- **Friendly but professional** tone
- **Explain the "why"** behind technical decisions
- **Visual progress indicators** - use emojis and clear status updates
- **Celebrate wins** - acknowledge when things work successfully
- **Patient with errors** - help debug step-by-step

### Problem Solving
- **Break complex problems** into simple steps
- **Provide alternatives** when first approach doesn't work
- **Show examples** of what good output looks like
- **Explain error messages** in plain English

## 🚀 DEVELOPMENT WORKFLOW

### Standard Process
1. **Understand the requirement** - clarify what user wants to achieve
2. **Break into steps** - show the step-by-step plan
3. **Build incrementally** - one step at a time with testing
4. **Integration testing** - ensure new code works with existing system
5. **Git commit** - proper version control with descriptive messages
6. **Documentation update** - update PROJECT_STATUS.md when needed

### Code Integration
1. **Check existing patterns** - follow established code style
2. **Import from existing modules** - reuse config, api, business_rules
3. **Add to main.py** - integrate into navigation if UI component
4. **Test thoroughly** - ensure no breaking changes
5. **Optimize for cost** - consider cost implications using cost_configuration

## 🎯 SUCCESS CRITERIA

### For Each Development Session
- [ ] Clear step-by-step progress
- [ ] Working code with no errors  
- [ ] Integration with existing system
- [ ] Git commit with descriptive message
- [ ] Updated documentation if needed
- [ ] User understands what was built and how to use it

### For Major Features
- [ ] Modular, maintainable code
- [ ] Comprehensive error handling
- [ ] Modern UI integration
- [ ] Cost optimization considered
- [ ] Business rules integration
- [ ] Testing completed
- [ ] Documentation updated

## 📝 QUICK REFERENCE

### Common Commands
```bash
# VS Code operations
code filename.py              # Open file in VS Code
code .                        # Open current directory

# Git workflow  
git status                    # Check changes
git add .                     # Stage all changes
git commit -m "message"       # Commit with message
git push origin main          # Push to GitHub

# Run application
python -m streamlit run src\main.py
```

### File Locations
- **Main app:** `src/main.py`
- **Cost system:** `src/communication_processing/`
- **API integrations:** `src/api/`
- **Business rules:** `src/business_rules/`
- **Status tracking:** `PROJECT_STATUS.md`

---

**Remember: The user is building a professional bank communication system. Every suggestion should consider:**
- **Regulatory compliance** (UK banking)
- **Cost optimization** (real cost savings)
- **User experience** (bank customers)
- **Scalability** (production use)
- **Maintainability** (modular code)