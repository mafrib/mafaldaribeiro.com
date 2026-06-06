import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    kind: z.string(),
    publishedAt: z.string().optional(),
    updatedAt: z.string().optional(),
    excerpt: z.string().optional(),
    navOrder: z.number().default(50),
    draft: z.boolean().default(false),
  }),
});

export const collections = { pages };
