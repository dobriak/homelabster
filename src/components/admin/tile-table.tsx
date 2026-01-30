/**
 * TileTable component - displays tiles in a table with edit/delete actions
 */

'use client';

import { useState } from 'react';
import Image from 'next/image';
import { toast } from 'sonner';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { TileForm } from './tile-form';
import { DeleteDialog } from './delete-dialog';
import { Edit, Trash2, ExternalLink } from 'lucide-react';
import type { Tile } from '@/types';

interface TileTableProps {
  tiles: Tile[];
  onUpdate: () => void;
}

export function TileTable({ tiles, onUpdate }: TileTableProps) {
  const [editingTile, setEditingTile] = useState<Tile | null>(null);
  const [deletingTile, setDeletingTile] = useState<Tile | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  async function handleDelete(tile: Tile) {
    const response = await fetch(`/api/tiles/${tile.id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete tile');
    }

    toast.success('Tile deleted successfully');
    onUpdate();
  }

  function handleEdit(tile: Tile) {
    setEditingTile(tile);
    setIsEditDialogOpen(true);
  }

  function handleEditSuccess() {
    setIsEditDialogOpen(false);
    setEditingTile(null);
    onUpdate();
  }

  if (tiles.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No tiles yet. Create your first tile to get started.
      </div>
    );
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Icon</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>URL</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Order</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tiles.map((tile) => (
              <TableRow key={tile.id}>
                <TableCell>
                  {tile.icon ? (
                    <div className="w-10 h-10 relative rounded-md overflow-hidden bg-muted">
                      <Image
                        src={tile.icon}
                        alt={tile.name}
                        fill
                        className="object-cover"
                        unoptimized
                      />
                    </div>
                  ) : (
                    <div className="w-10 h-10 rounded-md bg-muted" />
                  )}
                </TableCell>
                <TableCell className="font-medium">{tile.name}</TableCell>
                <TableCell>
                  <a
                    href={tile.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-primary hover:underline"
                  >
                    <span className="max-w-xs truncate">{tile.url}</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </TableCell>
                <TableCell className="max-w-xs truncate">
                  {tile.description || '-'}
                </TableCell>
                <TableCell>{tile.order}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(tile)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => setDeletingTile(tile)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Tile</DialogTitle>
          </DialogHeader>
          {editingTile && (
            <TileForm
              tile={editingTile}
              onSuccess={handleEditSuccess}
              onCancel={() => setIsEditDialogOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>

      <DeleteDialog
        open={!!deletingTile}
        onOpenChange={(open) => !open && setDeletingTile(null)}
        onConfirm={() => handleDelete(deletingTile!)}
        title="Delete Tile"
        description={`Are you sure you want to delete "${deletingTile?.name}"? This action cannot be undone.`}
      />
    </>
  );
}
