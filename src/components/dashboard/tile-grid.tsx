/**
 * TileGrid component - client component for filtering and displaying tiles
 */

'use client';

import { useState, useCallback } from 'react';
import { ServiceTile } from './service-tile';
import { SearchBar } from './search-bar';
import { EmptyState } from './empty-state';
import type { Tile } from '@/types';

interface TileGridProps {
  tiles: Tile[];
}

export function TileGrid({ tiles }: TileGridProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const filteredTiles = tiles.filter((tile) => {
    if (!searchQuery) return true;

    const query = searchQuery.toLowerCase();
    const matchesName = tile.name.toLowerCase().includes(query);
    const matchesDescription = tile.description?.toLowerCase().includes(query);

    return matchesName || matchesDescription;
  });

  if (tiles.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-6">
      <SearchBar onSearch={handleSearch} />

      {filteredTiles.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No services match your search.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredTiles.map((tile) => (
            <ServiceTile key={tile.id} tile={tile} />
          ))}
        </div>
      )}
    </div>
  );
}
