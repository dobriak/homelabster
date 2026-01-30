/**
 * ServiceTile component - displays a single service as a card
 */

import Link from 'next/link';
import Image from 'next/image';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ExternalLink } from 'lucide-react';
import type { Tile } from '@/types';

interface ServiceTileProps {
  tile: Tile;
}

export function ServiceTile({ tile }: ServiceTileProps) {
  return (
    <Link href={tile.url} target="_blank" rel="noopener noreferrer" className="group">
      <Card className="h-full transition-all hover:shadow-lg hover:scale-[1.02]">
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <CardTitle className="flex items-center gap-2 group-hover:text-primary transition-colors">
                {tile.name}
                <ExternalLink className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </CardTitle>
              {tile.description && (
                <CardDescription className="mt-2 line-clamp-2">
                  {tile.description}
                </CardDescription>
              )}
            </div>
            {tile.icon && (
              <div className="flex-shrink-0 w-12 h-12 relative rounded-md overflow-hidden bg-muted">
                <Image
                  src={tile.icon}
                  alt={`${tile.name} icon`}
                  fill
                  className="object-cover"
                  unoptimized
                />
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground truncate">{tile.url}</p>
        </CardContent>
      </Card>
    </Link>
  );
}
