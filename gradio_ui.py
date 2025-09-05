import gradio as gr
#import torch
import sys
import json
#sys.path.append(".")

#from main import AIArtFluxModel

# Define the base URL for images 
BASE_URL = "" # Please set base URL of SYNAPZ ! (###synapz.pro)

def load_styles_for_dataset(file_path="style.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_styles_json = json.load(f)
        
        dataset_samples = []
        style_lookup = {}
        
        for style in all_styles_json:
            if style.get('feature') in ['AI_Art_Changestyle', 'AI_Art']:
                name = style.get('name')
                prompt = style.get('prompt')
                feature = style.get('feature')
                after_url = style.get('image_after', {}).get('url')
                before_url = style.get('image_before', {}).get('url')

                if name and prompt and after_url and feature:
                    full_after_url = f"{BASE_URL}{after_url}"
                    full_before_url = f"{BASE_URL}{before_url}" if before_url else None
                    
                    dataset_samples.append([full_before_url, full_after_url, name, feature])
                    style_lookup[name] = {
                        'name': name, 
                        'prompt': prompt, 
                        'feature': feature,
                        'before_url': full_before_url, 
                        'after_url': full_after_url
                    }
            
        dataset_samples.sort(key=lambda x: (x[3], x[2]))        
        return dataset_samples, style_lookup
    
    except Exception as e:
        print(f"ERROR loading styles: {e}")
        return [], {}

def run():
    print("Loading model...")
    #model = AIArtFluxModel()
    print("Model loaded successfully.")
    
    print("Loading styles...")
    style_samples, style_map = load_styles_for_dataset()
    print(f"Loaded {len(style_samples)} styles.")

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        selected_style_state = gr.State(value=None)

        with gr.Tabs():
            # ================= STYLE TAB =================
            with gr.Tab("🎨 Style Library"):
                gr.Markdown("## Step 1: Upload & Generate")
                with gr.Row():
                    with gr.Column(scale=1):
                        image_input = gr.Image(type="pil", label="Upload Image")
                        prompt_display = gr.Textbox(label="Selected Style", interactive=False)
                        feature_display = gr.Textbox(label="Feature Type", interactive=False, visible=False)
                        submit_btn = gr.Button("✨ Generate Image!", variant="primary")
                    with gr.Column(scale=1):
                        output_image = gr.Image(type="pil", label="Result")
                        
                with gr.Row():
                    with gr.Column(scale=1):
                        reference_before = gr.Image(
                            label="Style Reference - Original",
                            interactive=False,
                            visible=False,
                            height=300,
                            width=300
                        )
                    with gr.Column(scale=1):
                        reference_after = gr.Image(
                            label="Style Reference - Styled",
                            interactive=False,
                            visible=False,
                            height=300,
                            width=300
                        )
                        
                gr.Markdown("## Step 2: Choose Your Favorite Style")
                style_gallery = gr.Dataset(
                    components=[
                        gr.Image(label="Before", type="filepath", interactive=False, visible=False),
                        gr.Image(label="After", type="filepath", interactive=False, visible=False),
                        gr.Textbox(label="Style", visible=False),
                        gr.Textbox(label="Feature", visible=False)
                    ],
                    samples=style_samples, 
                    label="Available Styles", 
                    samples_per_page=9,
                    elem_id="style_gallery"
                )

            # ================= CUSTOM PROMPT TAB =================
            with gr.Tab("✍️ Custom Prompt"):
                gr.Markdown("## Enter your own creative prompt")
                with gr.Row():
                    with gr.Column(scale=1):
                        image_input_custom = gr.Image(type="pil", label="Upload Image")
                        custom_feature_select = gr.Radio(
                            choices=["AI_Art", "AI_Art_Changestyle"], 
                            label="Select Feature Type", 
                            value="AI_Art"
                        )
                        custom_prompt_input = gr.Textbox(
                            label="Custom Prompt", 
                            placeholder="Enter your prompt here...", 
                            lines=4
                        )
                        submit_btn_custom = gr.Button("✨ Generate Image!", variant="primary")
                    with gr.Column(scale=1):
                        output_image_custom = gr.Image(type="pil", label="Result")

        # --- Event Handling ---
        def generate_image(image, style_info):
            if image is None: 
                raise gr.Error("Please upload an image to start!")
            final_prompt = style_info.get('prompt')
            style_name = style_info.get('name', 'Unknown')
            print(f"Generating with style: {style_name}")
            return None
            #return model.inference(image, final_prompt)

        submit_btn.click(
            fn=generate_image,
            inputs=[image_input, selected_style_state],
            outputs=output_image
        )
        
        def select_style_from_gallery(evt: gr.SelectData):
            selected_style_name = evt.value[2]
            full_style_info = style_map.get(selected_style_name)
            before_img = full_style_info.get('before_url') if full_style_info else None
            after_img = full_style_info.get('after_url') if full_style_info else None
            
            return (
                full_style_info, 
                gr.Textbox(value=full_style_info.get('name'), visible=True),
                gr.Textbox(value=full_style_info.get('feature', 'Unknown'), visible=True),
                gr.Image(value=before_img, visible=bool(before_img)),
                gr.Image(value=after_img, visible=bool(after_img))
            )
        
        style_gallery.select(
            fn=select_style_from_gallery,
            inputs=None,
            outputs=[selected_style_state, prompt_display, feature_display, reference_before, reference_after]
        )

        def generate_custom(image, feature, custom_prompt_text):
            if image is None: 
                raise gr.Error("Please upload an image to start!")
            if not custom_prompt_text or not custom_prompt_text.strip():
                raise gr.Error("Please enter a custom prompt!")
            print(f"Generating with feature={feature}, prompt={custom_prompt_text}")
            return None
            #return model.inference(image, custom_prompt_text)

        submit_btn_custom.click(
            fn=generate_custom,
            inputs=[image_input_custom, custom_feature_select, custom_prompt_input],
            outputs=output_image_custom
        )

    demo.launch(share=True, show_error=True)

if __name__ == "__main__":
    run()