const STORAGE_KEY = "novel2script_workspace";

export function getWorkspace(): string {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored && /^[\w一-鿿-]+$/.test(stored) && stored.length <= 100) {
    return stored;
  }
  return "";
}

export function setWorkspace(name: string): void {
  localStorage.setItem(STORAGE_KEY, name.trim());
}

export function clearWorkspace(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function isValidWorkspaceName(name: string): boolean {
  return /^[\w一-鿿-]+$/.test(name) && name.length >= 1 && name.length <= 100;
}
