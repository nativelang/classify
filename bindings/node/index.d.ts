export type Category = string | {
  id: string;
  description: string;
  examples?: readonly string[];
};

export function classify(text: string, categories: readonly Category[]): Promise<string | null>;
