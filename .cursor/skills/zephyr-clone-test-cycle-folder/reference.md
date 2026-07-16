# Zephyr clone test cycle folder — API reference

## Endpoints used (Cloud v2)

| Step | Method | Path | Body highlights |
|------|--------|------|-----------------|
| List folders | GET | `/folders?projectKey=&folderType=TEST_CYCLE` | Paginate `startAt` / `maxResults` |
| Create folder | POST | `/folders` | `projectKey`, `name`, `folderType: TEST_CYCLE`, optional `parentId` |
| List cycles | GET | `/testcycles?projectKey=&folderId=` | Paginated |
| Create cycle | POST | `/testcycles` | `projectKey`, `name`, `folderId`, `statusName: Not Executed` |
| List assignments | GET | `/testexecutions?testCycle={cycleKey}` | Filter by cycle key |
| Add test case to cycle | POST | `/testexecutions` | `projectKey`, `testCaseKey`, `testCycleKey`, `statusName: Not Executed` |

Official docs: [Zephyr Scale Cloud API](https://support.smartbear.com/zephyr-scale-cloud/api-docs/)

## What is not cloned

- Test execution history (status, comments, actual dates)
- Cycle/issue traceability links
- Test plan links
- Environments on executions
- Custom field values on executions (only default Not Executed)
- **Test cycles inside subfolder `Automation`** (folder shell only; default). Use `--include-automation-cycles` to clone them.

## Idempotency

Each run **creates new** folders and cycles. There is no upsert. Delete mistaken clones in the Zephyr UI before re-running with the same new name.
