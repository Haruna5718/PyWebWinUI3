<script lang="ts">
    export let data: { [key: string]: any };
</script>
<span style="
    flex-grow: {data.attr.size == null ? (data.attr.factor ?? 1) : 0};
    flex-shrink: {data.attr.size == null ? 1 : 0};
    flex-basis: {data.attr.size ?? 'auto'};">
    <slot />
</span>
