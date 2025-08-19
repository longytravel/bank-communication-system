"""
Enhanced Letter Scanner with Professional UI
Professional document management and classification system.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.api_manager import APIManager
from business_rules.engine import BusinessRulesEngine

class EnhancedLetterScanner:
    """Enhanced letter scanner with file upload and management capabilities."""
    
    def __init__(self, letters_dir: Path = None):
        """Initialize the enhanced letter scanner."""
        if letters_dir is None:
            letters_dir = Path("data/letters")
        
        self.letters_dir = letters_dir
        self.letters_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        self.demo_dir = self.letters_dir / "demo"
        self.uploaded_dir = self.letters_dir / "uploaded"
        self.demo_dir.mkdir(exist_ok=True)
        self.uploaded_dir.mkdir(exist_ok=True)
        
        self.api_manager = None
        self.supported_formats = ['.txt', '.md', '.docx', '.pdf']
        
        # Classification cache file
        self.cache_file = self.letters_dir / 'classification_cache.json'
        self.classification_cache = self._load_classification_cache()
    
    def _load_classification_cache(self) -> Dict:
        """Load existing classification cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_classification_cache(self):
        """Save classification cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.classification_cache, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Failed to save classification cache: {e}")
    
    def scan_all_letters(self) -> List[Dict]:
        """Scan all letters from all subdirectories."""
        letters = []
        
        # Scan all subdirectories
        for dir_path in [self.letters_dir, self.demo_dir, self.uploaded_dir]:
            for file_path in dir_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    # Determine source
                    if str(file_path).startswith(str(self.demo_dir)):
                        source = "demo"
                    elif str(file_path).startswith(str(self.uploaded_dir)):
                        source = "uploaded"
                    else:
                        source = "root"
                    
                    letter_info = {
                        'filename': file_path.name,
                        'filepath': str(file_path),
                        'source': source,
                        'size_bytes': file_path.stat().st_size,
                        'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'extension': file_path.suffix.lower(),
                        'classification': self.classification_cache.get(str(file_path), {})
                    }
                    letters.append(letter_info)
        
        # Sort by modification date (newest first)
        letters.sort(key=lambda x: x['modified_date'], reverse=True)
        
        return letters
    
    def upload_new_letter(self, uploaded_file, save_to_uploaded: bool = True) -> Optional[Path]:
        """Upload and save a new letter file."""
        try:
            # Determine save location
            save_dir = self.uploaded_dir if save_to_uploaded else self.letters_dir
            
            # Generate unique filename if file exists
            original_name = uploaded_file.name
            file_path = save_dir / original_name
            
            counter = 1
            while file_path.exists():
                name_parts = original_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{original_name}_{counter}"
                file_path = save_dir / new_name
                counter += 1
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            return file_path
            
        except Exception as e:
            st.error(f"Error uploading file: {e}")
            return None
    
    def create_new_letter_from_text(self, filename: str, content: str, source: str = "uploaded") -> Optional[Path]:
        """Create a new letter from text content."""
        try:
            # Determine save location
            if source == "demo":
                save_dir = self.demo_dir
            elif source == "uploaded":
                save_dir = self.uploaded_dir
            else:
                save_dir = self.letters_dir
            
            # Ensure .txt extension
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            file_path = save_dir / filename
            
            # Generate unique filename if file exists
            counter = 1
            while file_path.exists():
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{filename}_{counter}"
                file_path = save_dir / new_name
                counter += 1
            
            # Save the file
            file_path.write_text(content, encoding='utf-8')
            
            return file_path
            
        except Exception as e:
            st.error(f"Error creating letter: {e}")
            return None
    
    def delete_letter(self, file_path: str) -> bool:
        """Delete a letter file."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                
                # Remove from cache
                if file_path in self.classification_cache:
                    del self.classification_cache[file_path]
                    self._save_classification_cache()
                
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting file: {e}")
            return False
    
    def move_letter(self, file_path: str, destination: str) -> Optional[Path]:
        """Move a letter to a different directory."""
        try:
            source_path = Path(file_path)
            
            if destination == "demo":
                dest_dir = self.demo_dir
            elif destination == "uploaded":
                dest_dir = self.uploaded_dir
            else:
                dest_dir = self.letters_dir
            
            dest_path = dest_dir / source_path.name
            
            # Handle filename conflicts
            counter = 1
            while dest_path.exists():
                name_parts = source_path.name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{source_path.name}_{counter}"
                dest_path = dest_dir / new_name
                counter += 1
            
            shutil.move(str(source_path), str(dest_path))
            
            # Update cache with new path
            if file_path in self.classification_cache:
                self.classification_cache[str(dest_path)] = self.classification_cache[file_path]
                del self.classification_cache[file_path]
                self._save_classification_cache()
            
            return dest_path
            
        except Exception as e:
            st.error(f"Error moving file: {e}")
            return None
    
    def read_letter_content(self, file_path: Path) -> Optional[str]:
        """Read letter content based on file type."""
        try:
            if file_path.suffix.lower() in ['.txt', '.md']:
                return file_path.read_text(encoding='utf-8')
            
            elif file_path.suffix.lower() == '.docx':
                try:
                    from docx import Document
                    doc = Document(file_path)
                    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    st.warning("python-docx not installed. Please install it to read DOCX files.")
                    return None
            
            elif file_path.suffix.lower() == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        return text
                except ImportError:
                    st.warning("PyPDF2 not installed. Please install it to read PDF files.")
                    return None
            
            return None
            
        except Exception as e:
            st.error(f"Error reading {file_path.name}: {e}")
            return None
    
    def classify_letters(self, letters: List[Dict], force_reclassify: bool = False) -> Dict:
        """Classify letters using Claude API."""
        try:
            if self.api_manager is None:
                self.api_manager = APIManager()
        except Exception as e:
            st.error(f"Failed to initialize API: {e}")
            return {}
        
        classifications = {}
        unclassified_letters = []
        
        # Find letters that need classification
        for letter in letters:
            filepath = letter['filepath']
            
            # Check if already classified and not forcing reclassify
            if not force_reclassify and filepath in self.classification_cache:
                classifications[filepath] = self.classification_cache[filepath]
            else:
                unclassified_letters.append(letter)
        
        if not unclassified_letters:
            return classifications
        
        # Classification progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, letter in enumerate(unclassified_letters):
            filepath = letter['filepath']
            filename = letter['filename']
            
            status_text.text(f"Classifying {filename}...")
            progress_bar.progress((i + 1) / len(unclassified_letters))
            
            # Read letter content
            content = self.read_letter_content(Path(filepath))
            
            if content:
                try:
                    # Classify with Claude
                    classification = self.api_manager.classify_letter(content)
                    
                    if classification:
                        # Add additional metadata
                        classification['classified_date'] = datetime.now().isoformat()
                        classification['content_preview'] = content[:200] + "..." if len(content) > 200 else content
                        classification['word_count'] = len(content.split())
                        classification['source'] = letter['source']
                        
                        # Store in cache and results
                        self.classification_cache[filepath] = classification
                        classifications[filepath] = classification
                    
                    # Small delay to avoid rate limits
                    time.sleep(0.5)
                    
                except Exception as e:
                    st.warning(f"Failed to classify {filename}: {e}")
                    
                    # Create fallback classification
                    fallback = {
                        'classification': 'UNKNOWN',
                        'confidence': 0,
                        'reasoning': f'Classification failed: {str(e)}',
                        'classified_date': datetime.now().isoformat(),
                        'content_preview': content[:200] + "..." if len(content) > 200 else content,
                        'word_count': len(content.split()) if content else 0,
                        'source': letter['source']
                    }
                    
                    self.classification_cache[filepath] = fallback
                    classifications[filepath] = fallback
        
        # Save cache
        self._save_classification_cache()
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return classifications
    
    def get_letters_by_source(self, letters: List[Dict]) -> Dict[str, List[Dict]]:
        """Group letters by source."""
        grouped = {"demo": [], "uploaded": [], "root": []}
        
        for letter in letters:
            source = letter.get('source', 'root')
            grouped[source].append(letter)
        
        return grouped

def render_enhanced_letter_management():
    """Main function to render the enhanced letter management page."""
    
    # Create professional card HTML directly
    st.markdown("""
    <div class="pro-card">
        <div class="pro-card-header">
            <h3 class="pro-card-title">Letter Management</h3>
            <p class="pro-card-subtitle">Document classification and management system</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize scanner
    scanner = EnhancedLetterScanner()
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["Browse Letters", "Upload New", "Create Letter", "Manage"])
    
    with tab1:
        render_browse_letters_tab(scanner)
    
    with tab2:
        render_upload_letters_tab(scanner)
    
    with tab3:
        render_create_letter_tab(scanner)
    
    with tab4:
        render_manage_letters_tab(scanner)

def render_browse_letters_tab(scanner: EnhancedLetterScanner):
    """Render the browse letters tab."""
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Document Library
    </h3>
    """, unsafe_allow_html=True)
    
    # Scan letters
    letters = scanner.scan_all_letters()
    
    if not letters:
        st.info("No letters found. Upload documents or create new letters to get started.")
        return
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    letters_by_source = scanner.get_letters_by_source(letters)
    classified_count = sum(1 for letter in letters if letter['classification'])
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Documents</div>
            <div class="metric-value">{len(letters):,}</div>
            <div class="metric-delta">Active files</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Demo Letters</div>
            <div class="metric-value">{len(letters_by_source['demo']):,}</div>
            <div class="metric-delta">Sample documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Uploaded</div>
            <div class="metric-value">{len(letters_by_source['uploaded']):,}</div>
            <div class="metric-delta">User documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        classification_rate = (classified_count / len(letters) * 100) if letters else 0
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Classified</div>
            <div class="metric-value">{classified_count}/{len(letters)}</div>
            <div class="metric-delta">{classification_rate:.0f}% complete</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Classification controls
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        AI Classification
    </h4>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Classify New Letters", use_container_width=True):
            classify_letters(scanner, letters, force_reclassify=False)
    
    with col2:
        if st.button("Reclassify All", use_container_width=True):
            classify_letters(scanner, letters, force_reclassify=True)
    
    with col3:
        if st.button("Refresh List", use_container_width=True, type="secondary"):
            st.rerun()
    
    # Display letters table
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Document Overview
    </h4>
    """, unsafe_allow_html=True)
    
    # Create summary DataFrame
    letter_data = []
    
    for letter in letters:
        classification = letter['classification']
        
        letter_data.append({
            'Filename': letter['filename'],
            'Source': letter['source'].title(),
            'Classification': classification.get('classification', 'UNCLASSIFIED') if classification else 'UNCLASSIFIED',
            'Confidence': f"{classification.get('confidence', 0)}/10" if classification else '-',
            'Size': f"{letter['size_bytes']:,} bytes",
            'Modified': letter['modified_date'].strftime('%Y-%m-%d %H:%M'),
            'Word Count': classification.get('word_count', '-') if classification else '-'
        })
    
    if letter_data:
        df = pd.DataFrame(letter_data)
        st.dataframe(df, use_container_width=True, height=400)
    
    # Letter details
    if letters:
        render_letter_details_section(letters, scanner)

def render_upload_letters_tab(scanner: EnhancedLetterScanner):
    """Render the upload new letters tab."""
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Upload Documents
    </h3>
    <p style="color: #64748B; font-size: 0.875rem; margin-bottom: 1.5rem;">
        Upload letter files for AI classification and processing.
    </p>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['txt', 'md', 'docx', 'pdf'],
        accept_multiple_files=True,
        help="Supported formats: TXT, MD, DOCX, PDF"
    )
    
    if uploaded_files:
        st.markdown(f"""
        <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1rem 0;">
            Selected Files ({len(uploaded_files)})
        </h4>
        """, unsafe_allow_html=True)
        
        # Preview files
        for file in uploaded_files:
            with st.expander(f"{file.name} ({file.size:,} bytes)"):
                if file.type.startswith('text/') or file.name.endswith('.txt'):
                    try:
                        content = str(file.read(), "utf-8")
                        st.text_area("Preview:", content[:500] + "..." if len(content) > 500 else content, height=150, disabled=True)
                        file.seek(0)  # Reset file pointer
                    except:
                        st.warning("Could not preview this file")
                else:
                    st.info(f"File type: {file.type}")
        
        # Upload options
        col1, col2 = st.columns(2)
        
        with col1:
            save_location = st.selectbox(
                "Save to:",
                ["uploaded", "demo", "root"],
                help="Choose where to save the uploaded files"
            )
        
        with col2:
            auto_classify = st.checkbox(
                "Auto-classify after upload",
                value=True,
                help="Automatically classify uploaded letters"
            )
        
        # Upload button
        if st.button("Upload Files", type="primary", use_container_width=True):
            upload_results = []
            
            with st.spinner("Uploading files..."):
                for file in uploaded_files:
                    saved_path = scanner.upload_new_letter(file, save_to_uploaded=(save_location == "uploaded"))
                    
                    if saved_path:
                        upload_results.append({
                            'original_name': file.name,
                            'saved_path': saved_path,
                            'saved_name': saved_path.name
                        })
            
            if upload_results:
                st.success(f"Successfully uploaded {len(upload_results)} files")
                
                # Auto-classify if requested
                if auto_classify:
                    with st.spinner("Classifying uploaded documents..."):
                        letters = scanner.scan_all_letters()
                        new_letters = [l for l in letters if str(l['filepath']) in [str(r['saved_path']) for r in upload_results]]
                        
                        if new_letters:
                            classifications = scanner.classify_letters(new_letters, force_reclassify=True)
                            st.success(f"Classified {len(classifications)} documents")
                
                st.rerun()

def render_create_letter_tab(scanner: EnhancedLetterScanner):
    """Render the create new letter tab."""
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Create New Letter
    </h3>
    <p style="color: #64748B; font-size: 0.875rem; margin-bottom: 1.5rem;">
        Create a new letter document by typing or pasting content.
    </p>
    """, unsafe_allow_html=True)
    
    # Letter details
    col1, col2 = st.columns(2)
    
    with col1:
        filename = st.text_input(
            "Filename:",
            placeholder="my_new_letter.txt",
            help="Enter a filename (will add .txt if not specified)"
        )
    
    with col2:
        source = st.selectbox(
            "Save to:",
            ["uploaded", "demo", "root"],
            help="Choose where to save the new letter"
        )
    
    # Letter content
    letter_content = st.text_area(
        "Letter content:",
        height=300,
        placeholder="Enter your letter content here...",
        help="Enter the full content of your letter"
    )
    
    # Letter type hint (optional)
    letter_type_hint = st.selectbox(
        "Expected classification (optional):",
        ["", "REGULATORY", "PROMOTIONAL", "INFORMATION"],
        help="Optional hint for expected classification"
    )
    
    # Create button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Create Letter", type="primary", use_container_width=True, disabled=not filename or not letter_content):
            if filename and letter_content:
                # Create the letter
                saved_path = scanner.create_new_letter_from_text(filename, letter_content, source)
                
                if saved_path:
                    st.success(f"Created letter: {saved_path.name}")
                    
                    # Auto-classify the new letter
                    with st.spinner("Classifying new letter..."):
                        letters = scanner.scan_all_letters()
                        new_letter = next((l for l in letters if l['filepath'] == str(saved_path)), None)
                        
                        if new_letter:
                            classifications = scanner.classify_letters([new_letter], force_reclassify=True)
                            
                            if classifications:
                                classification = classifications.get(str(saved_path), {})
                                predicted_type = classification.get('classification', 'UNKNOWN')
                                confidence = classification.get('confidence', 0)
                                
                                st.success(f"Classified as: **{predicted_type}** (Confidence: {confidence}/10)")
                                
                                if letter_type_hint and letter_type_hint != predicted_type:
                                    st.warning(f"Note: Expected {letter_type_hint} but classified as {predicted_type}")
                    
                    time.sleep(2)
                    st.rerun()

def render_manage_letters_tab(scanner: EnhancedLetterScanner):
    """Render the manage letters tab."""
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
        Manage Documents
    </h3>
    """, unsafe_allow_html=True)
    
    letters = scanner.scan_all_letters()
    
    if not letters:
        st.info("No letters to manage.")
        return
    
    # Letter selection
    letter_options = [f"{letter['filename']} ({letter['source']}) - {letter['classification'].get('classification', 'UNCLASSIFIED') if letter['classification'] else 'UNCLASSIFIED'}" 
                     for letter in letters]
    
    selected_index = st.selectbox(
        "Select document:",
        range(len(letter_options)),
        format_func=lambda x: letter_options[x]
    )
    
    selected_letter = letters[selected_index]
    
    # Letter actions
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1rem 0;">
        Actions
    </h4>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("View Content", use_container_width=True):
            content = scanner.read_letter_content(Path(selected_letter['filepath']))
            if content:
                st.markdown("### Document Content")
                st.text_area(f"Content of {selected_letter['filename']}:", content, height=400, disabled=True)
    
    with col2:
        if st.button("Reclassify", use_container_width=True):
            classifications = scanner.classify_letters([selected_letter], force_reclassify=True)
            if classifications:
                st.success("Document reclassified")
                st.rerun()
    
    with col3:
        new_location = st.selectbox("Move to:", ["uploaded", "demo", "root"], key="move_location")
        if st.button("Move", use_container_width=True):
            new_path = scanner.move_letter(selected_letter['filepath'], new_location)
            if new_path:
                st.success(f"Moved to {new_location}")
                st.rerun()
    
    with col4:
        if st.button("Delete", use_container_width=True, type="secondary"):
            if scanner.delete_letter(selected_letter['filepath']):
                st.success("Document deleted")
                st.rerun()
    
    # Letter details
    if selected_letter['classification']:
        st.markdown("""
        <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
            Classification Details
        </h4>
        """, unsafe_allow_html=True)
        
        classification = selected_letter['classification']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Classification", classification.get('classification', 'Unknown'))
        
        with col2:
            st.metric("Confidence", f"{classification.get('confidence', 0)}/10")
        
        with col3:
            st.metric("Word Count", classification.get('word_count', 0))
        
        st.markdown("**Reasoning:**")
        st.info(classification.get('reasoning', 'No reasoning provided'))

def render_letter_details_section(letters: List[Dict], scanner: EnhancedLetterScanner):
    """Render letter details section."""
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1.5rem 0 1rem 0;">
        Document Details
    </h4>
    """, unsafe_allow_html=True)
    
    if not letters:
        return
    
    # Letter selector
    letter_options = [f"{letter['filename']} ({letter['source']}) - {letter['classification'].get('classification', 'UNCLASSIFIED') if letter['classification'] else 'UNCLASSIFIED'}" 
                     for letter in letters]
    
    selected_index = st.selectbox(
        "Select document to view details:",
        range(len(letter_options)),
        format_func=lambda x: letter_options[x]
    )
    
    selected_letter = letters[selected_index]
    classification = selected_letter['classification']
    
    # Display letter details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        details = {
            "Filename": selected_letter['filename'],
            "Source": selected_letter['source'].title(),
            "Size": f"{selected_letter['size_bytes']:,} bytes",
            "Modified": selected_letter['modified_date'].strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if classification:
            details.update({
                "Classification": classification.get('classification', 'Unknown'),
                "Confidence": f"{classification.get('confidence', 0)}/10",
                "Classified on": classification.get('classified_date', 'Unknown')
            })
        
        for key, value in details.items():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.25rem 0; border-bottom: 1px solid #E2E8F0;">
                <span style="font-weight: 500; color: #64748B; font-size: 0.875rem;">{key}:</span>
                <span style="color: #0F172A; font-size: 0.875rem;">{value}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Quick actions
        if st.button("View Content", use_container_width=True, key="details_view"):
            content = scanner.read_letter_content(Path(selected_letter['filepath']))
            if content:
                with st.expander("Document Content", expanded=True):
                    st.text_area("Content:", content, height=300, disabled=True)
    
   # Show classification reasoning
    if classification:
       st.markdown("""
       <h5 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1rem 0 0.5rem 0;">
           AI Analysis
       </h5>
       """, unsafe_allow_html=True)
       
       reasoning = classification.get('reasoning', 'No reasoning provided')
       st.info(reasoning)
       
       # Show key indicators if available
       indicators = classification.get('key_indicators', [])
       if indicators:
           st.markdown("""
           <h5 style="font-size: 0.875rem; font-weight: 600; color: #0F172A; margin: 1rem 0 0.5rem 0;">
               Key Indicators
           </h5>
           """, unsafe_allow_html=True)
           for indicator in indicators:
               st.markdown(f"• {indicator}")

def classify_letters(scanner: EnhancedLetterScanner, letters: List[Dict], force_reclassify: bool):
   """Helper function to classify letters with progress indication."""
   with st.container():
       st.markdown("""
       <div class="pro-card primary">
           <h3 style="margin-top: 0; color: white;">Running AI Classification</h3>
           <p style="color: rgba(255,255,255,0.9); margin-bottom: 0;">
               Claude is analyzing your letters for classification...
           </p>
       </div>
       """, unsafe_allow_html=True)
       
       classifications = scanner.classify_letters(letters, force_reclassify=force_reclassify)
       
       if classifications:
           st.success(f"Successfully classified {len(classifications)} letters!")
           st.rerun()

# Main function for testing
def main():
   """Main function for testing the letter scanner independently."""
   st.set_page_config(
       page_title="Letter Management",
       page_icon="📄",
       layout="wide"
   )
   
   st.title("Letter Management System")
   
   render_enhanced_letter_management()

if __name__ == "__main__":
   main()