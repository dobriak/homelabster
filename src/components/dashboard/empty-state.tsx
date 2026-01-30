/**
 * EmptyState component - shown when no tiles exist
 */

import { Package } from 'lucide-react';

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <Package className="h-16 w-16 text-muted-foreground/50 mb-4" />
      <h2 className="text-2xl font-semibold mb-2">No Services Yet</h2>
      <p className="text-muted-foreground max-w-md">
        Get started by adding your first service in the admin panel.
      </p>
    </div>
  );
}
