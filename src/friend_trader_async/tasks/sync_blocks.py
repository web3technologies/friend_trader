from celery import shared_task, chain, group

from django.conf import settings

from friend_trader_trader.models import Block
from friend_trader_async.tasks.perform_block_actions import  perform_block_actions_task
from friend_trader_async.tasks.update_latest_price import update_latest_price_task


@shared_task(
    bind=False, 
    name="sync_blocks_task"
    )
def sync_blocks_task(block_number=None):
    print("Syncing Blocks")
    initial_block_num = settings.INITIAL_BLOCK
    blocks_nums_stored = set(
        Block.objects.filter(block_number__gte=initial_block_num, block_number__lte=block_number)
        .exclude(date_sniffed=None)
        .order_by("block_number")
        .values_list("block_number", flat=True)
    )

    should_have_blocks = set(range(initial_block_num, block_number + 1))
    missing_blocks = list(should_have_blocks - blocks_nums_stored)
    missing_blocks.sort()
    if missing_blocks:
        print(f"Syncing blocks -- missing: {len(missing_blocks)}")
        block_actions_to_perform = []
        batch_count = 0
        for block_num in missing_blocks:
            block_actions_to_perform.append(
                chain(perform_block_actions_task.s(block_number=block_num), update_latest_price_task.s())
            )
            batch_count += 1
            if batch_count == 250:
                perform_many_block_actions = group(block_actions_to_perform)
                perform_many_block_actions.apply_async()
                block_actions_to_perform = []
                batch_count = 0
        perform_many_block_actions = group(block_actions_to_perform)
        perform_many_block_actions.apply_async()
    else:
        print(f"All blocks are synced and up to date")
    return missing_blocks