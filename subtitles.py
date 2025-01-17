import os
import subprocess
import re

# Define local yt-dlp path (Make sure yt-dlp.exe is in the same folder as this script)
YT_DLP_PATH = os.path.join(os.path.dirname(__file__), "yt-dlp.exe")  # Windows
# YT_DLP_PATH = os.path.join(os.path.dirname(__file__), "yt-dlp")  # Linux/Mac

# Function to download subtitles
def download_subtitles(youtube_url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)  # Create output folder if it doesn't exist
    output_path = os.path.join(output_dir, "%(title)s.%(ext)s")  

    # Use local yt-dlp instead of a global install
    command = [
        YT_DLP_PATH,  
        "--write-auto-sub",
        "--sub-lang", "en",
        "--convert-subs", "vtt",
        "-o", output_path,
        youtube_url
    ]
    
    subprocess.run(command, check=True)
    
    # Find the downloaded file
    for file in os.listdir(output_dir):
        if file.endswith(".vtt"):
            return os.path.join(output_dir, file)
    
    return None

# Function to clean up VTT subtitles
def convert_vtt_to_text(vtt_file, txt_file):
    with open(vtt_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    text_lines = []
    seen_lines = set()  # To prevent duplicates

    for line in lines:
        line = line.strip()

        # Remove "WEBVTT" headers and metadata
        if line.startswith(("WEBVTT", "Kind:", "Language:")):
            continue

        # Remove timestamp lines (full lines with --> format)
        if re.match(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line):
            continue

        # Remove inline timestamps like <00:00:10.599> inside sentences
        line = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", line)

        # Remove <c> tags from text
        line = re.sub(r"</?c>", "", line)  

        # Skip empty lines and duplicates
        if line and line not in seen_lines and "[Music]" not in line:
            seen_lines.add(line)
            text_lines.append(line)

    # Save cleaned text
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines))

    return txt_file

# Main function to process YouTube video
def extract_text_from_youtube(youtube_url):
    print(f"Downloading subtitles for: {youtube_url}")
    vtt_file = download_subtitles(youtube_url)

    if vtt_file:
        txt_file = vtt_file.replace(".vtt", ".txt")
        convert_vtt_to_text(vtt_file, txt_file)
        print(f"Extracted subtitles saved to: {txt_file}")

        # Open the file automatically
        os.system(f'start "" "{txt_file}"')  # Windows
        # os.system(f'xdg-open "{txt_file}"')  # Linux/Mac

    else:
        print("Failed to download subtitles.")

# Example usage
if __name__ == "__main__":
    youtube_link = input("Enter YouTube URL: ")
    extract_text_from_youtube(youtube_link)
