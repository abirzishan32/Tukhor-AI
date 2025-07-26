import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a timestamp for message display (shows time only)
 * @param timestamp - ISO string, Date object, or timestamp
 * @returns Formatted time string or empty string if invalid
 */
export function formatMessageTime(
  timestamp: string | Date | number | null | undefined
): string {
  try {
    if (!timestamp) return "";

    const date = new Date(timestamp);

    // Check if date is valid
    if (isNaN(date.getTime())) return "";

    return date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

/**
 * Format a timestamp for relative display (Today, Yesterday, etc.)
 * @param timestamp - ISO string, Date object, or timestamp
 * @returns Formatted relative date string or empty string if invalid
 */
export function formatRelativeDate(
  timestamp: string | Date | number | null | undefined
): string {
  try {
    if (!timestamp) return "";

    const date = new Date(timestamp);

    // Check if date is valid
    if (isNaN(date.getTime())) return "";

    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Today";
    if (diffDays === 2) return "Yesterday";
    if (diffDays <= 7) return `${diffDays - 1} days ago`;

    return date.toLocaleDateString();
  } catch {
    return "";
  }
}

/**
 * Format a full timestamp with both date and time
 * @param timestamp - ISO string, Date object, or timestamp
 * @returns Formatted full timestamp string or empty string if invalid
 */
export function formatFullTimestamp(
  timestamp: string | Date | number | null | undefined
): string {
  try {
    if (!timestamp) return "";

    const date = new Date(timestamp);

    // Check if date is valid
    if (isNaN(date.getTime())) return "";

    return date.toLocaleString([], {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

/**
 * Get a smart timestamp format based on recency
 * @param timestamp - ISO string, Date object, or timestamp
 * @returns Formatted timestamp (time for today, date for older)
 */
export function formatSmartTimestamp(
  timestamp: string | Date | number | null | undefined
): string {
  try {
    if (!timestamp) return "";

    const date = new Date(timestamp);

    // Check if date is valid
    if (isNaN(date.getTime())) return "";

    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    // If it's today, show time only
    if (diffDays === 1) {
      return formatMessageTime(timestamp);
    }

    // For older dates, show relative date
    return formatRelativeDate(timestamp);
  } catch {
    return "";
  }
}
