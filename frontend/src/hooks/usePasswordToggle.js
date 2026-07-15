import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export function usePasswordToggle() {
  const [isVisible, setIsVisible] = useState(false);

  const Icon = isVisible ? EyeOff : Eye;
  const inputType = isVisible ? "text" : "password";

  const toggleVisibility = () => setIsVisible(v => !v);

  return [inputType, Icon, toggleVisibility, isVisible];
}
