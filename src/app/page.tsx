/**
 * Dashboard page - displays service tiles with search
 */

import { getTiles, getSettings } from '@/lib/data';
import { TileGrid } from '@/components/dashboard/tile-grid';

export default async function Home() {
  const tiles = await getTiles();
  const settings = await getSettings();

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2">{settings.siteName}</h1>
          <p className="text-muted-foreground">Your homelab services dashboard</p>
        </header>

        <TileGrid tiles={tiles} />
      </div>
    </div>
  );
}
