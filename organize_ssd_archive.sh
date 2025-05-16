run_process_phase() {
    log_message "--- Starting PROCESS Phase ---"
    if [ ! -f "$DISCOVERY_LOG_FILE" ]; then log_error "Discovery log '$DISCOVERY_LOG_FILE' not found. Exiting."; exit 1; fi
    if [ ! -f "$CONFIRMATION_FILE_FOR_PROCESS_MODE" ]; then log_error "Confirmation file '$CONFIRMATION_FILE_FOR_PROCESS_MODE' not found. Exiting."; exit 1; fi

    if [ "$DRY_RUN" = false ]; then
        if [ ! -d "$BACKUP_ROOT_ABSOLUTE_PATH" ]; then mkdir -p "$BACKUP_ROOT_ABSOLUTE_PATH"; fi
        log_message "Initializing move action log at: $MOVE_ACTION_LOG_FILE"
        echo "# Move Actions Log - Started $(date)" > "$MOVE_ACTION_LOG_FILE"
        if [[ "$TARGET_FILE_TYPES" != "all" ]]; then echo "# Targeting file types: ${PARSED_TARGET_TYPES[*]}" >> "$MOVE_ACTION_LOG_FILE"; else echo "# Targeting ALL file types" >> "$MOVE_ACTION_LOG_FILE"; fi
        echo "# Format: mv -n \"source\" \"destination_directory/\"" >> "$MOVE_ACTION_LOG_FILE"
    fi

    local files_processed_count=0
    local batch_count=0
    local total_lines
    total_lines=$(grep -cvE '^#|^---$' "$DISCOVERY_LOG_FILE")
    log_message "Found $total_lines files to process in '$DISCOVERY_LOG_FILE' (for targeted types)."

    local line_count_debug=0 # Optional: for debugging the loop itself
    while IFS=$'\t' read -r original_file_path proposed_backup_file_path; do
        line_count_debug=$((line_count_debug + 1)) # Optional: debug
        # log_message "DEBUG: Processing line $line_count_debug from discovery log" # Optional: debug

        if [ -z "$original_file_path" ] || [ -z "$proposed_backup_file_path" ]; then
            log_warning "Skipping invalid line in discovery log: $original_file_path <TAB> $proposed_backup_file_path"
            continue
        fi

        if [ ! -f "$original_file_path" ]; then
            log_warning "Original file '$original_file_path' no longer exists. Skipping."
            continue
        fi

        local filename
        filename=$(basename "$original_file_path")
        local final_backup_destination_dir
        final_backup_destination_dir=$(dirname "$proposed_backup_file_path")

        # Batching / Per-file confirmation logic
        if [ "$PROCESS_BATCH_SIZE" -gt 0 ] && (( batch_count == 0 )); then
             if (( files_processed_count > 0 )); then # Avoid prompt before first file
                read -p "Processed $files_processed_count/$total_lines files. Continue with next batch of up to $PROCESS_BATCH_SIZE? [Y/n/q(uit)]: " batch_confirm
                case "$batch_confirm" in
                    n|N) log_message "User chose to pause batch processing. Exiting."; exit 0 ;;
                    q|Q) log_message "User chose to quit. Exiting."; exit 0 ;;
                    *) ;; # Default is Yes
                esac
             fi
        fi
        if [ "$PROCESS_BATCH_SIZE" -eq 0 ] && [ "$INTERACTIVE_FILE_CONFIRM" = true ]; then
             read -p "Process file ($((files_processed_count+1))/$total_lines): '$original_file_path' -> '$proposed_backup_file_path'? [Y/n/s(kip all)/q(uit)]: " file_confirm
             case "$file_confirm" in
                n|N) log_message "Skipping file by user choice: $original_file_path"; continue ;;
                s|S) log_message "User chose to skip all further per-file confirmations for this run."; INTERACTIVE_FILE_CONFIRM=false ;;
                q|Q) log_message "User chose to quit. Exiting."; exit 0 ;;
                *) ;; # Default is Yes
             esac
        fi

        if [ ! -d "$final_backup_destination_dir" ]; then
            if [ -f "$final_backup_destination_dir" ]; then
                log_warning "Cannot create type dir '$final_backup_destination_dir' (file exists). Skipping."
                continue
            fi
            log_action "Creating type directory: $final_backup_destination_dir"
            if [ "$DRY_RUN" = false ]; then
                mkdir -p "$final_backup_destination_dir"
                if [ $? -ne 0 ]; then log_warning "Failed to create '$final_backup_destination_dir'. Skipping '$filename'."; continue; fi
            fi
        fi

        log_action "Moving '$original_file_path' to '$final_backup_destination_dir/'"
        if [ "$DRY_RUN" = false ]; then
            if [ -f "$final_backup_destination_dir/$filename" ]; then
                log_warning "File '$filename' already exists in '$final_backup_destination_dir'. Skipping move."
            else
                mv -n "$original_file_path" "$final_backup_destination_dir/"
                if [ $? -ne 0 ]; then
                    log_warning "Failed to move '$original_file_path'. It might be in use or permissions issue."
                else
                    files_processed_count=$((files_processed_count + 1))
                fi
            fi
        else # If DRY_RUN is true for PROCESS phase
            files_processed_count=$((files_processed_count + 1))
        fi

        if [ "$PROCESS_BATCH_SIZE" -gt 0 ]; then
            batch_count=$(( (batch_count + 1) % PROCESS_BATCH_SIZE ))
        fi
    done < <(grep -vE '^#|^---$' "$DISCOVERY_LOG_FILE") # Ending with process substitution
    # ------ END OF MODIFIED PART ------

    # log_message "DEBUG: Loop finished. Final line_count_debug: $line_count_debug" # Optional: debug

    log_message "--- PROCESS Phase Complete ---"
    log_message "Successfully processed (for targeted types): $files_processed_count files."
} 