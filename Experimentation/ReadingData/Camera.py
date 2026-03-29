

    # CAMERA COMMENTED OUT FOR DESIGNING
    # Backup Camera Display
    # cam_frame = ttk.Frame(root)
    # cam_frame.pack(pady=20)

    # cam_label = ttk.Label(cam_frame, text="Backup Camera", font=("Arial", 16))
    # cam_label.pack()

    # video_label = tk.Label(cam_frame)
    # video_label.pack()

    # # Function to simulate black camera screen
    # def update_camera():
    #     # Create a black image (480x640)
    #     frame = cv2.UMat(480, 640, cv2.CV_8UC3)  # Create a black image
    #     img = PIL.Image.fromarray(frame.get())  # Convert it to PIL image
    #     img_tk = PIL.ImageTk.PhotoImage(image=img)  # Convert to Tkinter-compatible image

    #     video_label.img_tk = img_tk  # Keep reference to avoid garbage collection
    #     video_label.config(image=img_tk)  # Update the label to show the image

    #     root.after(50, update_camera)  # Refresh every 50ms

    # Start updating UI elements
    #update_display() Replaced with...